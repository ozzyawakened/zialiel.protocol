
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .transactions import Transaction

@dataclass
class Vertex:
    """
    Represents a single vertex in the DAG, containing a batch of transactions.
    """
    transactions: List[Transaction]
    parent_hashes: List[str]  # Hashes of parent vertices
    creator_id: str  # DID of the node that created this vertex
    timestamp: float = field(default_factory=time.time)
    signature: bytes = b''
    hash: str = field(init=False)

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates the SHA256 hash of the vertex's content."""
        block_string = f"{{'transactions': [tx.calculate_hash() for tx in self.transactions], 'parents': self.parent_hashes, 'creator': self.creator_id, 'timestamp': self.timestamp}}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash": self.hash,
            "transactions": [tx.calculate_hash() for tx in self.transactions],
            "parent_hashes": self.parent_hashes,
            "creator_id": self.creator_id,
            "timestamp": self.timestamp,
        }

@dataclass
class SuperVertex:
    """
    A special vertex that acts as a checkpoint for a set of vertices (a cohort).
    It contains dual Merkle roots for enhanced data integrity and structure validation.
    """
    cohort_hashes: List[str]  # Hashes of all vertices in the cohort
    parent_super_vertex_hash: str
    creator_id: str
    timestamp: float = field(default_factory=time.time)
    
    # Dual Merkle Roots
    transaction_merkle_root: str = field(init=False)
    structure_merkle_root: str = field(init=False)
    
    hash: str = field(init=False)
    signature: bytes = b''

    def __post_init__(self):
        self.transaction_merkle_root = self._calculate_merkle_root([h for h in self.cohort_hashes]) # Simplified: using cohort hashes as stand-ins for tx hashes
        self.structure_merkle_root = self._calculate_merkle_root([h for h in self.cohort_hashes])
        self.hash = self.calculate_hash()

    def _calculate_merkle_root(self, items: List[str]) -> str:
        """Calculates the Merkle root for a list of items (hashes)."""
        if not items:
            return hashlib.sha256(b'').hexdigest()

        hashed_items = [hashlib.sha256(item.encode()).hexdigest() for item in items]

        while len(hashed_items) > 1:
            if len(hashed_items) % 2 != 0:
                hashed_items.append(hashed_items[-1])  # Duplicate the last item if odd
            
            next_level = []
            for i in range(0, len(hashed_items), 2):
                combined = hashed_items[i] + hashed_items[i+1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashed_items = next_level
        
        return hashed_items[0]

    def calculate_hash(self) -> str:
        """Calculates the hash of the SuperVertex."""
        block_string = f"{{'parent': self.parent_super_vertex_hash, 'creator': self.creator_id, 'timestamp': self.timestamp, 'tx_root': self.transaction_merkle_root, 'struct_root': self.structure_merkle_root}}"
        return hashlib.sha256(block_string.encode()).hexdigest()
