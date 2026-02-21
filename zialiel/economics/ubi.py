# -------------------------------------
# 5. UBI DISTRIBUTION
# -------------------------------------

from .fees import FeeDistributor

class UBIDistributor:
    # ✅ BUG FIX: Pass the entire FeeDistributor instance (by reference) 
    # instead of just the initial value of ubi_fund.
    def __init__(self, fee_distributor: FeeDistributor):
        self.fee_distributor = fee_distributor
        self.verified_humans = set()  # DIDs that passed Proof of Personhood
        self.last_distribution = 0
        
    def verify_human(self, did: str, proof: str):
        """Proof of Personhood verification"""
        # 🚨 FLAW: This is not a real Sybil resistance mechanism.
        if len(proof) > 10:  # Simplified
            self.verified_humans.add(did)
            return True
        return False
    
    def distribute_ubi(self, current_time: int):
        """Distribute UBI weekly"""
        if current_time - self.last_distribution < 604800:  # 7 days
            return
        
        if not self.verified_humans:
            return
        
        # Access the fund directly from the fee distributor object
        ubi_fund = self.fee_distributor.ubi_fund
        if ubi_fund <= 0:
            return

        amount_per_human = ubi_fund / len(self.verified_humans)
        
        # In production: Distribute to each verified human
        print(f"Distributing {amount_per_human} to {len(self.verified_humans)} humans")
        
        # Reset the fund in the fee distributor
        self.fee_distributor.ubi_fund = 0
        self.last_distribution = current_time
