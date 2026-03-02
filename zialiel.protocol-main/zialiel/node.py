import logging
from typing import List, Dict, Optional

from .crypto_core.dag import DAG
from .crypto_core.consensus import QDBFT, CommitteeManager
from .crypto_core.real_mldsa_service import RealMLDSAService
from .crypto_core.transactions import Transaction
from .crypto_core.vertex import Vertex, SuperVertex
from .ledger.state import LedgerState
from .economics.fee_model import FeeModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Node:
    """
    Represents a single node (validator or user) in the Zialiel network.
    """
    def __init__(self, node_id: str, mldsa_service: RealMLDSAService, committee_manager: CommitteeManager, known_peers: Optional[Dict[str, bytes]] = None, shared_dag: Optional[DAG] = None):
        self.node_id = node_id
        self.mldsa_service = mldsa_service
        self.keypair = self.mldsa_service.generate_keypair()
        
        # Håndter known_peers
        if known_peers is None:
            self.known_peers = {}
        else:
            self.known_peers = known_peers
            
        self.known_peers[self.node_id] = self.keypair['public_key']

        # Håndter delt DAG
        if shared_dag is not None:
            self.dag = shared_dag
        else:
            self.dag = DAG()
        
        self.ledger_state = LedgerState()
        self.fee_model = FeeModel()
        self.consensus_engine = QDBFT(self.node_id, committee_manager, self.mldsa_service)
        self.mempool: List[Transaction] = []

    def create_transaction(self, recipient: str, amount: int, fee: int) -> Transaction:
        """
        Creates and signs a new transaction.
        """
        tx = Transaction(
            sender=self.node_id,
            recipient=recipient,
            amount=amount,
            fee=fee
        )
        message_to_sign = tx.to_message()
        tx.signature = self.mldsa_service.sign(self.keypair['private_key'], message_to_sign)
        self.mempool.append(tx)
        logging.info(f"Node {self.node_id} created transaction {tx.id[:8]} (amount: {amount}, fee: {fee})")
        return tx

    def create_vertex(self):
        """
        Creates a new vertex from transactions in the mempool.
        """
        if not self.mempool:
            logging.info(f"Node {self.node_id} has no transactions in mempool to create a vertex.")
            return None

        parent_hashes = self.dag.get_tips() or ['genesis']
        vertex = Vertex(
            transactions=list(self.mempool),
            parent_hashes=parent_hashes,
            creator_id=self.node_id
        )
        vertex.signature = self.mldsa_service.sign(self.keypair['private_key'], vertex.hash.encode())
        
        tx_count = len(self.mempool)
        self.mempool.clear()
        
        if self.dag.add_vertex(vertex):
            logging.info(f"Node {self.node_id} created vertex {vertex.hash[:8]} with {tx_count} transactions.")
        else:
            logging.error(f"Node {self.node_id} failed to add vertex {vertex.hash[:8]} to DAG.")
            
        return vertex

    def process_finalized_super_vertex(self, super_vertex: SuperVertex):
        """
        Processes a finalized super-vertex, applying its transactions to the ledger.
        """
        logging.info(f"Node {self.node_id} processing finalized super-vertex {super_vertex.hash[:8]}.")
        
        total_transactions = 0
        successful_transactions = 0
        
        for vertex_hash in super_vertex.cohort_hashes:
            vertex = self.dag.get_vertex(vertex_hash)
            if not vertex:
                logging.warning(f"Vertex {vertex_hash[:8]} from finalized super-vertex not found in DAG.")
                continue

            for tx in vertex.transactions:
                total_transactions += 1
                
                # Get sender's public key
                sender_pub_key = self.known_peers.get(tx.sender)
                if not sender_pub_key:
                    logging.error(f"Public key for sender {tx.sender} not found. Skipping transaction {tx.id[:8]}.")
                    continue

                # Verify signature
                is_valid = self.mldsa_service.verify(sender_pub_key, tx.to_message(), tx.signature)
                if not is_valid:
                    logging.error(f"Invalid signature for transaction {tx.id[:8]}. Skipping.")
                    continue

                # Apply transaction to ledger
                success = self.ledger_state.apply_transaction(tx.sender, tx.recipient, tx.amount, tx.fee)
                
                if success:
                    successful_transactions += 1
                    # Distribute fees
                    fee_breakdown = self.fee_model.get_fee_breakdown(tx.fee)
                    self.ledger_state.distribute_fee(fee_breakdown)
                    logging.debug(f"Transaction {tx.id[:8]} applied: {tx.sender} -> {tx.recipient} amount={tx.amount} fee={tx.fee}")
                else:
                    logging.error(f"Transaction {tx.id[:8]} failed: insufficient funds or invalid accounts")

        logging.info(f"Node {self.node_id} processed {successful_transactions}/{total_transactions} transactions successfully.")

    def get_balance(self, account_id: str) -> int:
        """Get balance for an account."""
        return self.ledger_state.get_balance(account_id)

    def get_pool_balances(self) -> Dict[str, int]:
        """Get all fee pool balances."""
        return {
            "validator": self.ledger_state.validator_share_pool,
            "ubi": self.ledger_state.ubi_share_pool,
            "carbon": self.ledger_state.carbon_share_pool,
            "gratitude": self.ledger_state.gratitude_share_pool
        }
