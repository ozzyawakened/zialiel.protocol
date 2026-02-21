# -------------------------------------
# 4. FEE ARCHITECTURE + DISTRIBUTION
# -------------------------------------

from zialiel.core.transactions import Transaction

class FeeDistributor:
    def __init__(self):
        self.validator_pool = 0
        self.ubi_fund = 0
        self.common_pool = 0
        self.culture_fund = 0
        self.gratitude_pool = 0
        self.carbon_fund = 0
        
    def distribute(self, tx: Transaction):
        """Distribute fees according to split configuration"""
        total_fee = tx.fee
        
        # Default split if none provided
        split = tx.fee_split or {
            "validator_pool": 0.5,
            "ubi_fund": 0.2,
            "common_pool": 0.15,
            "culture_fund": 0.05,
            "gratitude_pool": 0.05,
            "carbon_fund": 0.05
        }
        
        for fund, percentage in split.items():
            amount = total_fee * percentage
            if fund == "validator_pool":
                self.validator_pool += amount
            elif fund == "ubi_fund":
                self.ubi_fund += amount
            elif fund == "common_pool":
                self.common_pool += amount
            elif fund == "culture_fund":
                self.culture_fund += amount
            elif fund == "gratitude_pool":
                self.gratitude_pool += amount
            elif fund == "carbon_fund":
                self.carbon_fund += amount
        
        # Handle gratitude flag
        if tx.gratitude:
            self.gratitude_pool += tx.amount * 0.001  # Tiny micro-donation
        
        # Handle carbon offset
        if tx.offset_carbon:
            self.carbon_fund += tx.amount * 0.002  # 0.2% for offset
