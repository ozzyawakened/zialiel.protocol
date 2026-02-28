
import logging
from typing import List, Dict, Any
from collections import defaultdict

from .vertex import SuperVertex
from .dag import DAG
from .real_mldsa_service import RealMLDSAService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CommitteeManager:
    """
    Manages the validator committee, including selection, rotation, and history.
    """
    def __init__(self, initial_committee: List[str]):
        self.current_committee: List[str] = initial_committee
        self.committee_history: List[List[str]] = [initial_committee]
        logging.info(f"CommitteeManager initialized with committee: {self.current_committee}")

    def get_current_committee(self) -> List[str]:
        return self.current_committee

    def rotate_committee(self, new_committee: List[str]):
        """Updates the committee and records the change in history."""
        self.current_committee = new_committee
        self.committee_history.append(new_committee)
        logging.info(f"Committee rotated. New committee: {self.current_committee}")

class QDBFT:
    """
    Quantum-resistant Delegated Byzantine Fault Tolerance (QDBFT) Consensus Engine.

    This engine is responsible for finalizing SuperVertices through a multi-round
    voting process among a designated committee.
    """
    def __init__(self, node_id: str, committee_manager: CommitteeManager, mldsa_service: RealMLDSAService):
        self.node_id = node_id
        self.committee_manager = committee_manager
        self.mldsa_service = mldsa_service
        self.pending_votes: Dict[str, Dict[str, bytes]] = defaultdict(dict)  # super_vertex_hash -> {voter_id: signature}
        self.finalized_super_vertices: Set[str] = set()

    def propose_super_vertex(self, super_vertex: SuperVertex, private_key: bytes):
        """
        A committee member proposes a new SuperVertex to be finalized.
        The proposal is essentially the first vote.
        """
        if self.node_id not in self.committee_manager.get_current_committee():
            logging.warning(f"Node {self.node_id} is not in the current committee. Cannot propose.")
            return

        logging.info(f"Node {self.node_id} is proposing super-vertex {super_vertex.hash}.")
        self.cast_vote(super_vertex.hash, private_key)

    def cast_vote(self, super_vertex_hash: str, private_key: bytes):
        """
        A committee member casts a vote for a super-vertex.
        The vote is a signature on the super-vertex hash.
        """
        if self.node_id not in self.committee_manager.get_current_committee():
            logging.warning(f"Node {self.node_id} is not in the current committee. Cannot vote.")
            return

        if super_vertex_hash in self.finalized_super_vertices:
            logging.warning(f"Super-vertex {super_vertex_hash} is already finalized. Ignoring vote.")
            return

        signature = self.mldsa_service.sign(private_key, super_vertex_hash.encode())
        self.pending_votes[super_vertex_hash][self.node_id] = signature
        logging.info(f"Node {self.node_id} cast a vote for super-vertex {super_vertex_hash}.")

        self._check_for_finality(super_vertex_hash)

    def _check_for_finality(self, super_vertex_hash: str):
        """
        Checks if a super-vertex has enough votes to be finalized.
        """
        committee = self.committee_manager.get_current_committee()
        votes = self.pending_votes.get(super_vertex_hash, {})
        
        # BFT requires > 2/3 of votes. For simplicity, we'll use ceil(2/3 * N).
        required_votes = int(len(committee) * 2 / 3) + 1

        if len(votes) >= required_votes:
            # In a real system, we would need to verify all signatures here.
            # We assume they are valid for this simulation.
            self.finalized_super_vertices.add(super_vertex_hash)
            logging.info(f"FINALIZED: Super-vertex {super_vertex_hash} has been finalized with {len(votes)} votes.")
            
            # Clean up votes for the finalized block
            del self.pending_votes[super_vertex_hash]
