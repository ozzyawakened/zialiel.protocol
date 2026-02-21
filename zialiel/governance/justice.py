# -------------------------------------
# 6. RESTORATIVE JUSTICE
# -------------------------------------

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

# Assuming Reputation is defined elsewhere, e.g., in zialiel.core.identity
# from zialiel.core.identity import Reputation

class DisputeStatus(Enum):
    MEDIATION = 1
    JURY = 2
    RESOLVED = 3
    REHABILITATION = 4

@dataclass
class Dispute:
    id: str
    complainant_did: str
    respondent_did: str
    amount_in_question: float
    description: str
    status: DisputeStatus
    created_at: int
    
    # ✅ BUG FIX: Fields with default values must come after non-default fields.
    mediator_did: Optional[str] = None
    proposed_resolution: Optional[Dict] = None
    jury: List[str] = field(default_factory=list)
    restitution_escrow: float = 0
    resolved_at: Optional[int] = None

class RestorativeJustice:
    def __init__(self):
        self.disputes = {}
        self.rehabilitation_paths = {}  # DID -> Rehabilitation record
    
    def create_dispute(self, dispute: Dispute):
        self.disputes[dispute.id] = dispute
        return dispute.id
    
    def select_mediator(self, dispute_id: str, mediator_pool: List['Reputation']):
        """Select mediator based on reputation"""
        dispute = self.disputes.get(dispute_id)
        if not dispute:
            return
        
        # Choose mediator with highest relevant reputation
        mediators = sorted(mediator_pool, key=lambda r: r.score, reverse=True)
        if mediators:
            dispute.mediator_did = mediators[0].did
            dispute.status = DisputeStatus.MEDIATION
    
    def propose_resolution(self, dispute_id: str, resolution: dict):
        dispute = self.disputes.get(dispute_id)
        if dispute and dispute.status == DisputeStatus.MEDIATION:
            dispute.proposed_resolution = resolution
    
    def accept_resolution(self, dispute_id: str, party: str, current_time_func):
        dispute = self.disputes.get(dispute_id)
        if not dispute:
            return
        
        # Simplified: Both parties need to accept
        # In production: Track acceptances separately
        dispute.status = DisputeStatus.RESOLVED
        dispute.resolved_at = current_time_func()
        
        # Execute restitution if any
        if 'restitution_amount' in dispute.proposed_resolution:
            dispute.restitution_escrow = dispute.proposed_resolution['restitution_amount']
            # Transfer from respondent to escrow, then to complainant
        
        # Begin rehabilitation if applicable
        if dispute.proposed_resolution.get('rehabilitation', False):
            self.rehabilitation_paths[dispute.respondent_did] = {
                'start_date': current_time_func(),
                'probation_end': current_time_func() + 15552000,  # 6 months
                'requirements': dispute.proposed_resolution.get('requirements', [])
            }
    
    def complete_rehabilitation(self, did: str, current_time_func):
        """Mark rehabilitation as complete and restore reputation"""
        if did in self.rehabilitation_paths:
            record = self.rehabilitation_paths[did]
            if current_time_func() > record['probation_end']:
                # All requirements checked (simplified)
                del self.rehabilitation_paths[did]
                # Reputation gradually restored elsewhere
                return True
        return False
