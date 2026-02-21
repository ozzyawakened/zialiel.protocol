
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LedgerState:
    """
    A placeholder class representing the ledger state, including account balances and special funds.
    This is a simplified in-memory representation for the simulation.
    """
    def __init__(self):
        self.balances = defaultdict(int)
        self.ubi_fund = 0
        logging.info("LedgerState initialized with empty balances and ubi_fund.")

    def credit(self, address: str, amount: int):
        """
        Credits a specified amount to an address.

        Args:
            address (str): The recipient's address.
            amount (int): The amount to credit.
        """
        if amount < 0:
            logging.warning(f"Attempted to credit a negative amount {-amount} to {address}. Operation aborted.")
            return
            
        self.balances[address] += amount
        logging.info(f"Credited {amount} to {address}. New balance: {self.balances[address]}.")

    def debit(self, address: str, amount: int) -> bool:
        """
        Debits a specified amount from an address.

        Args:
            address (str): The sender's address.
            amount (int): The amount to debit.

        Returns:
            bool: True if the debit was successful, False otherwise.
        """
        if amount < 0:
            logging.warning(f"Attempted to debit a negative amount {-amount} from {address}. Operation aborted.")
            return False

        if self.balances[address] >= amount:
            self.balances[address] -= amount
            logging.info(f"Debited {amount} from {address}. New balance: {self.balances[address]}.")
            return True
        else:
            logging.warning(f"Debit failed: Insufficient funds for {address}. Has {self.balances[address]}, needs {amount}.")
            return False
