# zialiel/ledger/ledger.py

from collections import defaultdict
from zialiel.crypto_core.transactions import Transaction

class Ledger:
    """
    Records the consequences of finalized transactions.
    Tracks coin balances for all Decentralized Identifiers (DIDs).
    """
    def __init__(self):
        self.balances = defaultdict(float)

    def apply_transaction(self, tx: Transaction):
        """
        Updates balances based on a single finalized transaction.
        This method should only be called after a transaction has achieved
        finality through the crypto_core consensus.
        """
        # Ensure the sender has enough balance
        # Note: In a real system, this check happens at multiple stages.
        # Here, we do a final check before committing to the ledger.
        if self.balances[tx.sender_did] < tx.amount + tx.fee:
            # This should ideally not happen if consensus is working correctly
            print(f"Error: Insufficient funds for sender {tx.sender_did} in transaction {tx.id}")
            return False

        # Debit sender
        self.balances[tx.sender_did] -= (tx.amount + tx.fee)

        # Credit recipient
        self.balances[tx.recipient_did] += tx.amount
        
        # Note: The fee is removed from the sender's balance but not yet credited
        # to anyone. The FeeDistributor will handle the allocation of the
        # collected fees from the transactions.

        return True

    def get_balance(self, did: str) -> float:
        """Returns the balance for a given DID."""
        return self.balances.get(did, 0.0)
