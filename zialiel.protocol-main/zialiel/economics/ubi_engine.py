
import logging
from typing import Dict, Any
from zialiel.ledger.state import LedgerState

# --- Constants ---
UBI_DISTRIBUTION_INTERVAL_VERTICES = 1000
UBI_VERIFICATION_REQUIRED = True
MAX_UBI_PER_DISTRIBUTION = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UBIEngine:
    """
    Manages the periodic distribution of Universal Basic Income (UBI) to verified human accounts.
    """

    def __init__(self, ledger_state: LedgerState):
        """
        Initializes the UBIEngine.

        Args:
            ledger_state (LedgerState): An instance of the ledger state to interact with.
        """
        self.ledger_state = ledger_state
        self.verified_humans: Dict[str, bool] = {}
        self.finalized_vertex_count: int = 0
        self.total_distributed: int = 0
        logging.info("UBIEngine initialized.")

    def register_human(self, address: str, proof_of_humanity: str) -> bool:
        """
        Registers and verifies an address as belonging to a human.

        In this mock implementation, verification is a simple check on the proof string.

        Args:
            address (str): The address to register.
            proof_of_humanity (str): A string representing proof of humanity.

        Returns:
            bool: True if registration is successful, False otherwise.
        """
        if self.verified_humans.get(address):
            logging.warning(f"Address {address} is already registered as a verified human.")
            return False

        if UBI_VERIFICATION_REQUIRED:
            # Mock verification: check for non-empty string longer than 10 chars
            if not proof_of_humanity or len(proof_of_humanity) <= 10:
                logging.error(f"Invalid proof of humanity for {address}. Registration failed.")
                return False
        
        self.verified_humans[address] = True
        logging.info(f"Address {address} successfully registered as a verified human.")
        return True

    def on_vertex_finalized(self, vertex_hash: str) -> None:
        """
        Callback executed when a new vertex is finalized by the consensus mechanism.
        
        This method increments the vertex counter and triggers the UBI distribution
        if the interval is reached.

        Args:
            vertex_hash (str): The hash of the finalized vertex (for logging).
        """
        self.finalized_vertex_count += 1
        # Use modulo to ensure distribution happens exactly on the interval
        if self.finalized_vertex_count % UBI_DISTRIBUTION_INTERVAL_VERTICES == 0 and self.finalized_vertex_count > 0:
            logging.info(f"Vertex {self.finalized_vertex_count} finalized. Triggering UBI distribution.")
            self._distribute_ubi()

    def _distribute_ubi(self) -> None:
        """
        Handles the core logic of distributing UBI from the dedicated fund.
        
        This is a private method called by on_vertex_finalized.
        """
        ubi_fund_balance = self.ledger_state.ubi_fund
        num_verified_humans = len(self.verified_humans)

        if ubi_fund_balance <= 0:
            logging.warning("UBI distribution skipped: UBI fund is empty or has a negative balance.")
            return

        if num_verified_humans == 0:
            logging.warning("UBI distribution skipped: No verified humans registered.")
            return

        # Calculate the amount per person, capped by the max
        per_person_amount = min(ubi_fund_balance // num_verified_humans, MAX_UBI_PER_DISTRIBUTION)

        if per_person_amount <= 0:
            logging.warning(f"UBI distribution skipped: Calculated amount per person is zero or less.")
            return
        
        total_to_distribute = per_person_amount * num_verified_humans

        # Double-check we have enough funds
        if self.ledger_state.ubi_fund < total_to_distribute:
             logging.error(f"CRITICAL: UBI fund has insufficient balance for distribution. Fund: {self.ledger_state.ubi_fund}, Needed: {total_to_distribute}")
             return

        logging.info(f"Starting UBI distribution. Fund: {ubi_fund_balance}, Humans: {num_verified_humans}, Amount/Person: {per_person_amount}")

        # Distribute the funds
        for address in self.verified_humans.keys():
            self.ledger_state.credit(address, per_person_amount)
        
        # Deduct the total from the UBI fund
        self.ledger_state.ubi_fund -= total_to_distribute
        self.total_distributed += total_to_distribute

        logging.info(f"UBI distribution complete. Total distributed: {total_to_distribute}. New UBI fund balance: {self.ledger_state.ubi_fund}.")

    def get_verified_human_count(self) -> int:
        """Returns the number of verified human accounts."""
        return len(self.verified_humans)

    def get_distribution_stats(self) -> Dict[str, Any]:
        """
        Provides statistics about the UBI distribution process.

        Returns:
            Dict[str, Any]: A dictionary containing key stats.
        """
        stats = {
            "total_distributed": self.total_distributed,
            "verified_humans": self.get_verified_human_count(),
            "next_distribution_in": UBI_DISTRIBUTION_INTERVAL_VERTICES - (self.finalized_vertex_count % UBI_DISTRIBUTION_INTERVAL_VERTICES),
            "ubi_fund_balance": self.ledger_state.ubi_fund
        }
        return stats
