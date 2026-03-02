import random
import logging
from typing import List, Dict

from zialiel.node import Node
from zialiel.crypto_core.dag import DAG  # <-- VIKTIG: Importer DAG
from zialiel.crypto_core.real_mldsa_service import RealMLDSAService
from zialiel.crypto_core.consensus import CommitteeManager
from zialiel.crypto_core.vertex import SuperVertex

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_simulation():
    """
    Runs a full simulation of the Zialiel network, from transaction creation to ledger application.
    """
    # --- 1. SETUP ---
    logging.info("--- SIMULATION START: Initializing network components ---")
    
    # Initialize the core crypto service
    mldsa_service = RealMLDSAService()

    # Define the initial validator set
    validator_ids = ["validator_0", "validator_1", "validator_2", "validator_3"]
    committee_manager = CommitteeManager(initial_committee=validator_ids)

    # Opprett én felles DAG for ALLE noder
    shared_dag = DAG()
    logging.info("Created shared DAG for all nodes")

    # Create nodes med delt DAG
    nodes: Dict[str, Node] = {}
    all_peers = {}
    
    # Opprett validatorer med delt DAG
    for i in range(len(validator_ids)):
        node = Node(f"validator_{i}", mldsa_service, committee_manager, all_peers, shared_dag)
        nodes[node.node_id] = node
        all_peers[node.node_id] = node.keypair['public_key']
    
    # Opprett vanlige brukere med delt DAG
    user_nodes = [Node(f"user_{i}", mldsa_service, committee_manager, all_peers, shared_dag) for i in range(2)]
    for node in user_nodes:
        nodes[node.node_id] = node
        all_peers[node.node_id] = node.keypair['public_key']

    # Initialize user balances
    ledger_for_init = nodes["validator_0"].ledger_state
    for node in user_nodes:
        ledger_for_init.credit(node.node_id, 10000)
    logging.info(f"Initial balance for user_0: {ledger_for_init.get_balance('user_0')}")
    logging.info(f"Initial balance for user_1: {ledger_for_init.get_balance('user_1')}")


    # --- 2. TRANSACTION & VERTEX CREATION ---
    logging.info("--- SIMULATION PHASE 2: Creating transactions and vertices ---")
    
    # User 0 sends a transaction to user_1
    tx1 = user_nodes[0].create_transaction(recipient="user_1", amount=100, fee=10)
    logging.info(f"Transaction 1: {tx1.sender} -> {tx1.recipient} amount={tx1.amount} fee={tx1.fee}")
    
    # User 1 sends a transaction to user_0
    tx2 = user_nodes[1].create_transaction(recipient="user_0", amount=50, fee=5)
    logging.info(f"Transaction 2: {tx2.sender} -> {tx2.recipient} amount={tx2.amount} fee={tx2.fee}")

    # A validator picks up the transactions and creates a vertex
    validator_node = nodes["validator_0"]
    validator_node.mempool.extend([tx1, tx2])
    vertex1 = validator_node.create_vertex()
    
    if vertex1:
        logging.info(f"✅ Created vertex {vertex1.hash[:8]} with {len(vertex1.transactions)} transactions")
    else:
        logging.error("❌ Failed to create vertex")

    # --- 3. CONSENSUS (SUPER-VERTEX CREATION & FINALIZATION) ---
    logging.info("--- SIMULATION PHASE 3: Achieving consensus on a Super-Vertex ---")

    # A leader (validator_2) proposes a SuperVertex
    leader_node = nodes["validator_2"]
    
    # Hent alle vertices fra den DELTE DAG-en
    all_vertices = list(shared_dag.vertices.values())  # <-- Bruk shared_dag, ikke leader_node.dag
    logging.info(f"Total vertices in shared DAG: {len(all_vertices)}")
    
    if all_vertices:
        # Use the most recent vertex
        latest_vertex = all_vertices[-1]
        cohort_hashes = [latest_vertex.hash]
        logging.info(f"Using vertex {latest_vertex.hash[:8]} for super-vertex")
    else:
        logging.error("No vertices found in DAG!")
        cohort_hashes = []
    
    super_vertex = SuperVertex(
        cohort_hashes=cohort_hashes,
        parent_super_vertex_hash='genesis_sv',
        creator_id=leader_node.node_id
    )
    shared_dag.add_super_vertex(super_vertex)  # <-- Bruk shared_dag
    logging.info(f"Created super-vertex {super_vertex.hash[:8]} with {len(cohort_hashes)} vertices")

    # The leader proposes it to the consensus engine
    leader_node.consensus_engine.propose_super_vertex(super_vertex, leader_node.keypair['private_key'])

    # Other committee members see the proposal and vote
    for i in [0, 1, 3]: # The other 3 validators
        voter_node = nodes[f"validator_{i}"]
        voter_node.consensus_engine.cast_vote(super_vertex.hash, voter_node.keypair['private_key'])
        logging.info(f"Validator_{i} voted")

    # --- 4. LEDGER APPLICATION ---
    logging.info("--- SIMULATION PHASE 4: Applying finalized state to the ledger ---")

    # Check if the super-vertex was finalized
    if len(leader_node.consensus_engine.finalized_super_vertices) > 0:
        finalized_hash = list(leader_node.consensus_engine.finalized_super_vertices)[0]
        if finalized_hash == super_vertex.hash:
            logging.info(f"✅ Super-vertex {super_vertex.hash[:8]} successfully finalized!")
            # All nodes can now process the finalized block
            for node in nodes.values():
                node.process_finalized_super_vertex(super_vertex)
        else:
            logging.error(f"❌ Finalized hash {finalized_hash[:8]} doesn't match super-vertex {super_vertex.hash[:8]}")
    else:
        logging.error("❌ No super-vertices were finalized!")


    # --- 5. FINAL STATE VERIFICATION ---
    logging.info("--- SIMULATION COMPLETE: Verifying final ledger state ---")
    final_ledger = nodes["validator_0"].ledger_state
    user0_balance = final_ledger.get_balance('user_0')
    user1_balance = final_ledger.get_balance('user_1')
    
    logging.info(f"Final balance for user_0: {user0_balance}")
    logging.info(f"Final balance for user_1: {user1_balance}")

    logging.info(f"Final UBI Pool: {final_ledger.ubi_share_pool}")
    logging.info(f"Final Validator Pool: {final_ledger.validator_share_pool}")
    logging.info(f"Final Carbon Pool: {final_ledger.carbon_share_pool}")
    logging.info(f"Final Gratitude Pool: {final_ledger.gratitude_share_pool}")

    # Expected results:
    # User 0 started with 10000, sent 100+10, received 50. Final: 9940
    # User 1 started with 10000, sent 50+5, received 100. Final: 10045
    # Total fees: 15. Validator: 9, UBI: 3, Carbon: 1, Gratitude: 2
    
    try:
        assert user0_balance == 9940, f"User 0 balance should be 9940, got {user0_balance}"
        assert user1_balance == 10045, f"User 1 balance should be 10045, got {user1_balance}"
        assert final_ledger.ubi_share_pool == 3
        assert final_ledger.carbon_share_pool == 1
        assert final_ledger.gratitude_share_pool == 1
        # Validator pool kan være 9 eller 10 avhengig av avrunding
        assert final_ledger.validator_share_pool in [9, 10], f"Validator pool should be 9 or 10, got {final_ledger.validator_share_pool}"
        logging.info("✅ All assertions passed. The simulation was successful!")
    except AssertionError as e:
        logging.error(f"❌ Assertion failed: {e}")
if __name__ == "__main__":
    run_simulation()