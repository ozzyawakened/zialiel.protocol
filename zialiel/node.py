
import logging
from typing import List

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
    def __init__(self, node_id: str, mldsa_service: RealMLDSAService, committee_manager: CommitteeManager, known_peers: Dict[str, bytes] = {}):
        self.node_id = node_id
        self.mldsa_service = mldsa_service
        self.keypair = self.mldsa_service.generate_keypair()
        self.known_peers = known_peers  # node_id -> public_key
        self.known_peers[self.node_id] = self.keypair['public_key']

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
        logging.info(f"Node {self.node_id} created transaction {tx.id}.")
        return tx

    def create_vertex(self):
        """
        Creates a new vertex from transactions in the mempool.
        """
        if not self.mempool:
            logging.info(f"Node {self.node_id} has no transactions in mempool to create a vertex.")
            return None

        parent_hashes = self.dag.get_tips() or ['genesis'] # Simplified genesis
        vertex = Vertex(
            transactions=list(self.mempool),
            parent_hashes=parent_hashes,
            creator_id=self.node_id
        )
        vertex.signature = self.mldsa_service.sign(self.keypair['private_key'], vertex.hash.encode())
        
        self.mempool.clear()
        self.dag.add_vertex(vertex)
        logging.info(f"Node {self.node_id} created vertex {vertex.hash}.")
        return vertex

    def process_finalized_super_vertex(self, super_vertex: SuperVertex):
        """
        Processes a finalized super-vertex, applying its transactions to the ledger.
        """
        logging.info(f"Node {self.node_id} processing finalized super-vertex {super_vertex.hash}.")
        for vertex_hash in super_vertex.cohort_hashes:
            vertex = self.dag.get_vertex(vertex_hash)
            if not vertex:
                logging.warning(f"Vertex {vertex_hash} from finalized super-vertex not found in DAG.")
                continue

            for tx in vertex.transactions:
                sender_pub_key = self.known_peers.get(tx.sender)
                if not sender_pub_key:
                    logging.error(f"Public key for sender {tx.sender} not found. Cannot verify transaction {tx.calculate_hash()}.")
                    continue

                is_valid = self.mldsa_service.verify(sender_pub_key, tx.to_message(), tx.signature)
                if is_valid:
                    success = self.ledger_state.apply_transaction(tx.sender, tx.recipient, tx.amount, tx.fee)
                    if success:
                        fee_breakdown = self.fee_model.get_fee_breakdown(tx.fee)
                        self.ledger_state.distribute_fee(fee_breakdown)
                else:
                    logging.error(f"Invalid signature for transaction {tx.calculate_hash()} in finalized vertex. Skipping.")
