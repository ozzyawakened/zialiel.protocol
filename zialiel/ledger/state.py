
import logging
from collections import defaultdict
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LedgerState:
    """
    Represents the state of the ledger, including all account balances and system-wide funds.
    This is a simplified in-memory representation. In a real system, this would be
    backed by a persistent, auditable database.
    """
    def __init__(self):
        # Account balances for all users/contracts
        self.balances = defaultdict(int)

        # --- System-wide Fee Pools ---
        # Renaming ubi_fund for consistency, it's one of the four pools.
        self.ubi_share_pool = 0
        self.validator_share_pool = 0
        self.carbon_share_pool = 0
        self.gratitude_share_pool = 0
        
        logging.info("LedgerState initialized with empty balances and fee pools.")

    def apply_transaction(self, sender: str, recipient: str, amount: int, fee: int) -> bool:
        """
        Applies a transaction to the ledger state by debiting the sender and crediting the recipient.
        The fee is also deducted from the sender.

        Args:
            sender (str): The address of the transaction sender.
            recipient (str): The address of the transaction recipient.
            amount (int): The amount of the transaction.
            fee (int): The fee for the transaction.

        Returns:
            bool: True if the transaction was applied successfully, False otherwise.
        """
        total_debit = amount + fee
        if self.balances[sender] < total_debit:
            logging.warning(f"Transaction failed: Insufficient funds for sender {sender}. Has {self.balances[sender]}, needs {total_debit}.")
            return False

        self.balances[sender] -= total_debit
        self.balances[recipient] += amount
        logging.info(f"Applied transaction: {sender} -> {recipient} ({amount}). New balances: Sender={self.balances[sender]}, Recipient={self.balances[recipient]}")
        return True

    def distribute_fee(self, fee_breakdown: Dict[str, int]):
        """
        Distributes a collected fee into the four system-wide pools.

        Args:
            fee_breakdown (Dict[str, int]): A dictionary containing the shares for each pool.
        """
        self.validator_share_pool += fee_breakdown.get("validator_share", 0)
        self.ubi_share_pool += fee_breakdown.get("ubi_share", 0)
        self.carbon_share_pool += fee_breakdown.get("carbon_share", 0)
        self.gratitude_share_pool += fee_breakdown.get("gratitude_share", 0)
        logging.info(f"Fee distributed. Current pools: UBI={self.ubi_share_pool}, Validator={self.validator_share_pool}, Carbon={self.carbon_share_pool}, Gratitude={self.gratitude_share_pool}")


    def credit(self, address: str, amount: int):
        """
        Directly credits a specified amount to an address. Used for UBI payouts and other system-level transfers.

        Args:
            address (str): The recipient's address.
            amount (int): The amount to credit.
        """
        if amount < 0:
            logging.warning(f"Attempted to credit a negative amount {-amount} to {address}. Operation aborted.")
            return
            
        self.balances[address] += amount
        logging.info(f"Credited {amount} to {address}. New balance: {self.balances[address]}.")

    def get_balance(self, address: str) -> int:
        """
        Retrieves the balance of a given address.

        Args:
            address (str): The address to query.

        Returns:
            int: The balance of the address.
        """
        return self.balances.get(address, 0)
