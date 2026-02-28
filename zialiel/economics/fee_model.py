
import logging
import math
from typing import Dict

# --- Constants ---
BASE_FEE = 10
CONGESTION_MULTIPLIER_MAX = 5.0
CONGESTION_THRESHOLD_VERTICES = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeeModel:
    """
    Defines the transaction fee calculation logic for the Zialiel network.
    """

    def calculate_fee(self, amount: int, mempool_size: int, priority: str) -> int:
        """
        Calculates the total fee for a transaction based on its amount, network congestion, and priority.

        Args:
            amount (int): The transaction amount. Although not used in this version, it's kept for future fee models.
            mempool_size (int): The current number of transactions in the mempool (unconfirmed vertices).
            priority (str): The transaction priority ("low", "normal", "high").

        Returns:
            int: The calculated transaction fee, as an integer.
        """
        fee = float(BASE_FEE)

        # 1. Apply priority multiplier
        if priority == "high":
            fee *= 2.0
        elif priority == "normal":
            fee *= 1.5
        elif priority == "low":
            fee *= 1.0
        else:
            logging.warning(f"Unknown priority '{priority}'. Defaulting to low priority.")
            priority = "low"
            fee *= 1.0
        
        logging.info(f"Fee after priority '{priority}' multiplier: {fee}")

        # 2. Apply congestion pricing
        if mempool_size > CONGESTION_THRESHOLD_VERTICES:
            congestion_range = (CONGESTION_THRESHOLD_VERTICES * 10) - CONGESTION_THRESHOLD_VERTICES
            current_congestion = mempool_size - CONGESTION_THRESHOLD_VERTICES
            
            # Calculate how far into the congestion zone we are (0.0 to 1.0)
            congestion_factor = min(1.0, current_congestion / congestion_range)
            
            # Scale multiplier linearly from 1.0 to CONGESTION_MULTIPLIER_MAX
            congestion_multiplier = 1.0 + congestion_factor * (CONGESTION_MULTIPLIER_MAX - 1.0)
            
            # Cap the multiplier
            congestion_multiplier = min(congestion_multiplier, CONGESTION_MULTIPLIER_MAX)
            
            fee *= congestion_multiplier
            logging.info(f"Mempool size {mempool_size} exceeds threshold {CONGESTION_THRESHOLD_VERTICES}. Applying congestion multiplier {congestion_multiplier:.2f}. New fee: {fee}")

        final_fee = max(1, math.ceil(fee))
        logging.info(f"Final calculated fee: {final_fee}")
        return final_fee

    def estimate_confirmation_time(self, priority: str, current_tps: float) -> str:
        """
        Provides a human-readable estimate for transaction confirmation time.

        Args:
            priority (str): The transaction priority.
            current_tps (float): The current network throughput in transactions per second.

        Returns:
            str: A string estimating the confirmation time.
        """
        if priority == "high" and current_tps > 100:
            return "~2 seconds"
        if priority == "normal" and current_tps > 50:
            return "~5 seconds"
        
        return "~15 seconds"

    def get_fee_breakdown(self, total_fee: int) -> Dict[str, int]:
        """
        Splits the total fee into shares for various network stakeholders.

        The split is 60/20/10/10 for validators, UBI, carbon offsets, and gratitude.
        Any remainder from integer division is given to the validator.

        Args:
            total_fee (int): The total transaction fee.

        Returns:
            Dict[str, int]: A dictionary detailing the fee distribution.
        """
        if total_fee < 1:
            return {"validator_share": 0, "ubi_share": 0, "carbon_share": 0, "gratitude_share": 0}

        validator_share = int(total_fee * 0.6)
        ubi_share = int(total_fee * 0.2)
        carbon_share = int(total_fee * 0.1)
        gratitude_share = int(total_fee * 0.1)

        # Ensure the sum is exactly total_fee by giving the remainder to the validator
        current_total = validator_share + ubi_share + carbon_share + gratitude_share
        remainder = total_fee - current_total
        validator_share += remainder

        breakdown = {
            "validator_share": validator_share,
            "ubi_share": ubi_share,
            "carbon_share": carbon_share,
            "gratitude_share": gratitude_share
        }
        
        assert sum(breakdown.values()) == total_fee
        logging.info(f"Fee breakdown for {total_fee}: {breakdown}")
        return breakdown
