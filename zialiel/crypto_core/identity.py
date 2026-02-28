# -------------------------------------
# 2. IDENTITY + REPUTATION
# -------------------------------------

from dataclasses import dataclass
from typing import List

@dataclass
class DID:
    """Decentralized Identifier"""
    id: str
    public_key: str
    created_at: int
    credentials: List[dict]  # Verifiable credentials from attestors
    
@dataclass
class Reputation:
    did: str
    score: float  # 0-100
    factors: dict
        # - transaction_history: float
        # - dispute_resolutions: float
        # - attestations_received: float
        # - governance_participation: float
        # - public_goods_contributions: float
        # - gratitude_received: float
    last_updated: int
    
    def decay(self):
        """Reputation gradually decays without activity"""
        self.score *= 0.99  # 1% decay per period
    
    def boost(self, factor: str, amount: float):
        if factor in self.factors:
            self.factors[factor] += amount
            self.recalculate()
    
    def recalculate(self):
        weighted = (
            self.factors['transaction_history'] * 0.2 +
            self.factors['dispute_resolutions'] * 0.15 +
            self.factors['attestations_received'] * 0.25 +
            self.factors['governance_participation'] * 0.1 +
            self.factors['public_goods_contributions'] * 0.2 +
            self.factors['gratitude_received'] * 0.1
        )
        self.score = min(100, weighted)
