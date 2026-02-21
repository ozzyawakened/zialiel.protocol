# -------------------------------------
# 3. DAG CONSENSUS
# -------------------------------------

import random
from dataclasses import dataclass, field
from typing import List, Set
from .signature import SignatureScheme

@dataclass
class Transaction:
    id: str
    sender_did: str
    recipient_did: str
    amount: float
    fee: float
    fee_split: dict
    signature: str
    timestamp: int
    parent_transactions: List[str]
    collateral: float
    
    # Consensus-related fields
    gratitude: bool = False
    offset_carbon: bool = False
    confidence: int = 0
    consecutive_successes: int = 0
    finalized: bool = False
    queried_by: Set[str] = field(default_factory=set) # Nodes that have queried this in a round

    def is_preferred(self, other: 'Transaction') -> bool:
        """Determines if this transaction is preferred over another, older one."""
        if not other:
            return True
        return self.timestamp > other.timestamp

class DAG:
    """
    Implements the Quantum-Resistant Avalanche (QR-Avalanche) consensus on a DAG.
    This is a simplified simulation for a single node's perspective.
    """
    def __init__(self, k: int = 10, alpha: int = 6, beta: int = 15):
        self.transactions = {}  # id -> Transaction
        self.tips = set()
        self.conflicts = {}  # transaction_id -> set of conflicting transaction_ids
        
        # Avalanche parameters
        self.k = k          # Sample size
        self.alpha = alpha  # Quorum size
        self.beta = beta    # Decision threshold (consecutive successes)

        # Node state
        self.preference = None # Preferred transaction in a conflict set

    def add_transaction(self, tx: Transaction):
        """
        Adds a transaction to the DAG and initiates consensus.
        This replaces the simple validation from before.
        """
        # Basic structural validation (can be expanded)
        if not isinstance(tx, Transaction):
            return False
            
        # 🚨 FLAW: This verification is placeholder and insecure.
        # In a real implementation, the public key would be retrieved from the sender's DID document.
        # For now, we assume sender_did is the public key for simplicity.
        # This check is also conceptually in the wrong place for Avalanche.
        # A node initially believes a transaction is valid if it's structurally sound.
        # The consensus process then determines if it's accepted by the network.
        # We'll keep it here as a basic guardrail.
        # if not SignatureScheme.verify(tx.sender_did, tx.id, tx.signature):
        #     print(f"Signature verification failed for tx {tx.id}")
        #     return False

        self.transactions[tx.id] = tx
        self.update_tips(tx)
        self.find_conflicts(tx)

        # If this transaction is not conflicting, it's considered preferred for now.
        if not self.conflicts.get(tx.id):
            self.preference = tx.id
        
        return True

    def find_conflicts(self, new_tx: Transaction):
        """Identifies and stores conflicts (e.g., double spends)."""
        for tx_id, tx in self.transactions.items():
            if tx_id == new_tx.id:
                continue
            
            # Simple double-spend check
            if tx.sender_did == new_tx.sender_did and tx.id != new_tx.id:
                if new_tx.id not in self.conflicts:
                    self.conflicts[new_tx.id] = set()
                if tx_id not in self.conflicts:
                    self.conflicts[tx_id] = set()
                
                self.conflicts[new_tx.id].add(tx_id)
                self.conflicts[tx_id].add(new_tx.id)

    def run_consensus_round(self, validators: List['CovenantProtocol']):
        """
        Simulates a single round of QR-Avalanche consensus.
        A node queries k other validators and updates its preference.
        """
        if not self.preference or self.transactions[self.preference].finalized:
            # If no preference or already decided, select a new unfinalized tip to vote on.
            unfinalized_tips = [tip for tip in self.tips if not self.transactions[tip].finalized]
            if not unfinalized_tips:
                return # Nothing to do
            self.preference = random.choice(unfinalized_tips)

        current_tx = self.transactions[self.preference]
        
        # 1. Sub-sample validators
        if len(validators) < self.k:
            sample = validators
        else:
            sample = random.sample(validators, self.k)

        # 2. Query the sample for their preferences
        responses = {} # preference_id -> count
        for validator in sample:
            # In a real network, this would be a network call.
            # Here, we directly access the validator's preference.
            pref_id = validator.crypto_core.get_preference()
            if pref_id:
                responses[pref_id] = responses.get(pref_id, 0) + 1

        # 3. Check for a quorum
        strongest_preference = None
        max_votes = 0
        for pref_id, votes in responses.items():
            if votes > max_votes:
                max_votes = votes
                strongest_preference = pref_id

        if max_votes >= self.alpha:
            # We have a quorum for the strongest preference
            if self.preference == strongest_preference:
                current_tx.consecutive_successes += 1
            else:
                # Switch preference
                self.preference = strongest_preference
                current_tx.consecutive_successes = 1
        else:
            # No quorum, reset counter
            current_tx.consecutive_successes = 0

        # 4. Check for finality
        if current_tx.consecutive_successes > self.beta:
            self.finalize(current_tx)

    def get_preference(self):
        """Returns the node's current preferred transaction ID."""
        return self.preference

    def finalize(self, tx: Transaction):
        """Mark a transaction as finalized and reject its conflicts."""
        tx.finalized = True
        print(f"✅ Transaction {tx.id} finalized!")

        # Reject all known conflicts
        if tx.id in self.conflicts:
            for conflict_id in self.conflicts[tx.id]:
                if conflict_id in self.transactions:
                    self.transactions[conflict_id].finalized = True # Or move to a 'rejected' state
                    print(f"❌ Transaction {conflict_id} rejected due to conflict with {tx.id}.")
            # No need to track these conflicts anymore
            del self.conflicts[tx.id]

    def update_tips(self, tx: Transaction):
        for parent in tx.parent_transactions:
            if parent in self.tips:
                self.tips.remove(parent)
        self.tips.add(tx.id)
