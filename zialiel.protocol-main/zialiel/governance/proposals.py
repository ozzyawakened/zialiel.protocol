# zialiel/governance/proposals.py
"""
Governance Proposals with Wisdom Oracle Integration
Extends the restorative justice system with spiritual governance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import time
import logging

from .wisdom_oracle import WisdomOracle, ProposalVerdict
from .justice import RestorativeJustice

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProposalType(Enum):
    """Types of governance proposals"""
    PARAMETER_CHANGE = "parameter_change"      # Change network parameters
    CONSTITUTIONAL = "constitutional"           # Change core principles
    TREASURY = "treasury"                       # Allocate funds
    JUSTICE_APPEAL = "justice_appeal"           # Appeal a dispute ruling
    CULTURAL = "cultural"                        # Rituals, celebrations, gratitude
    WISDOM_UPDATE = "wisdom_update"              # Add new wisdom traditions

class ProposalStatus(Enum):
    DRAFT = "draft"
    WISDOM_REVIEW = "wisdom_review"              # Being analyzed by oracle
    COMMUNITY_VOTE = "community_vote"            # Open for voting
    PASSED = "passed"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"

@dataclass
class Proposal:
    """A governance proposal with wisdom oracle integration"""
    id: str
    title: str
    description: str
    proposer_did: str
    proposal_type: ProposalType
    created_at: int = field(default_factory=time.time)
    status: ProposalStatus = ProposalStatus.DRAFT
    
    # Parameters being changed (for parameter_change type)
    parameter_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Treasury allocation (for treasury type)
    recipient_did: Optional[str] = None
    amount: Optional[int] = None
    
    # Justice appeal (for justice_appeal type)
    dispute_id: Optional[str] = None
    appeal_reason: Optional[str] = None
    
    # Wisdom oracle results
    wisdom_verdict: Optional[ProposalVerdict] = None
    
    # Voting
    votes_for: Dict[str, int] = field(default_factory=dict)  # voter_did -> weight
    votes_against: Dict[str, int] = field(default_factory=dict)
    delegated_votes: Dict[str, str] = field(default_factory=dict)  # voter_did -> delegate_did
    
    voting_start: Optional[int] = None
    voting_end: Optional[int] = None
    voting_power_snapshot: Dict[str, int] = field(default_factory=dict)  # voter_did -> voting power
    
    # Results
    passed: Optional[bool] = None
    implemented_at: Optional[int] = None
    implementation_results: Dict[str, Any] = field(default_factory=dict)

class GovernanceEngine:
    """
    Complete governance system integrating Wisdom Oracle with community voting.
    """
    
    def __init__(self, wisdom_oracle: WisdomOracle, justice_system: RestorativeJustice):
        self.wisdom_oracle = wisdom_oracle
        self.justice_system = justice_system
        self.proposals: Dict[str, Proposal] = {}
        self.voting_power_cache: Dict[str, int] = {}  # DID -> voting power (based on stake, reputation)
        self.execution_history: List[Dict] = []
        logging.info("GovernanceEngine initialized with Wisdom Oracle integration")
    
    def create_proposal(self, 
                       title: str,
                       description: str,
                       proposer_did: str,
                       proposal_type: ProposalType,
                       parameter_changes: Dict[str, Any] = None,
                       recipient_did: str = None,
                       amount: int = None,
                       dispute_id: str = None,
                       appeal_reason: str = None) -> str:
        """
        Create a new governance proposal and submit it to Wisdom Oracle.
        """
        import uuid
        proposal_id = f"prop_{uuid.uuid4().hex[:8]}"
        
        # Determine affected principles based on proposal content
        affected_principles = self._extract_principles(title, description, proposal_type)
        
        proposal = Proposal(
            id=proposal_id,
            title=title,
            description=description,
            proposer_did=proposer_did,
            proposal_type=proposal_type,
            created_at=time.time(),
            status=ProposalStatus.WISDOM_REVIEW,
            parameter_changes=parameter_changes or {},
            recipient_did=recipient_did,
            amount=amount,
            dispute_id=dispute_id,
            appeal_reason=appeal_reason
        )
        
        self.proposals[proposal_id] = proposal
        logging.info(f"Proposal {proposal_id} created: {title}")
        
        # Automatically submit to Wisdom Oracle
        self._submit_to_wisdom_oracle(proposal_id, affected_principles)
        
        return proposal_id
    
    def _extract_principles(self, title: str, description: str, proposal_type: ProposalType) -> List[str]:
        """Extract ethical principles affected by this proposal"""
        principles = []
        
        # Map proposal types to principles
        type_principles = {
            ProposalType.CONSTITUTIONAL: ["justice", "stewardship", "dignity"],
            ProposalType.PARAMETER_CHANGE: ["fairness", "efficiency"],
            ProposalType.TREASURY: ["stewardship", "generosity"],
            ProposalType.JUSTICE_APPEAL: ["justice", "compassion", "restoration"],
            ProposalType.CULTURAL: ["gratitude", "community"],
            ProposalType.WISDOM_UPDATE: ["wisdom", "truth"]
        }
        
        principles.extend(type_principles.get(proposal_type, []))
        
        # Check description for principle keywords
        keyword_map = {
            "justice": ["justice", "fair", "rights", "equality"],
            "compassion": ["compassion", "mercy", "kindness", "care"],
            "stewardship": ["stewardship", "environment", "future", "sustainable"],
            "gratitude": ["gratitude", "thank", "celebration", "honor"],
            "freedom": ["freedom", "liberty", "autonomy", "choice"],
            "community": ["community", "together", "collective", "shared"],
            "truth": ["truth", "honest", "transparent", "verify"]
        }
        
        text = (title + " " + description).lower()
        for principle, keywords in keyword_map.items():
            if any(k in text for k in keywords):
                if principle not in principles:
                    principles.append(principle)
        
        return principles
    
    def _submit_to_wisdom_oracle(self, proposal_id: str, principles: List[str]):
        """Submit proposal to Wisdom Oracle for ethical analysis"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return
        
        # Determine if this is constitutional
        is_constitutional = (proposal.proposal_type == ProposalType.CONSTITUTIONAL)
        
        # Get oracle verdict
        verdict = self.wisdom_oracle.analyze_proposal(
            proposal_title=proposal.title,
            proposal_description=proposal.description,
            affected_principles=principles,
            is_constitutional=is_constitutional
        )
        
        proposal.wisdom_verdict = verdict
        
        # If wisdom oracle strongly rejects, proposal dies immediately
        if verdict.confidence < 0.3 and not is_constitutional:
            proposal.status = ProposalStatus.REJECTED
            proposal.passed = False
            logging.info(f"Proposal {proposal_id} rejected by Wisdom Oracle (confidence: {verdict.confidence:.2f})")
        else:
            # Move to community vote
            proposal.status = ProposalStatus.COMMUNITY_VOTE
            self._start_voting(proposal_id)
            logging.info(f"Proposal {proposal_id} passed Wisdom Oracle review. Moving to community vote.")
    
    def _start_voting(self, proposal_id: str):
        """Initialize voting period for a proposal"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return
        
        # Voting period: 7 days for normal, 14 days for constitutional
        voting_days = 14 if proposal.proposal_type == ProposalType.CONSTITUTIONAL else 7
        
        proposal.voting_start = time.time()
        proposal.voting_end = proposal.voting_start + (voting_days * 24 * 60 * 60)
        
        # Snapshot voting power (simplified - in production, get from ledger)
        # This is where you'd query stake, reputation, etc.
        self._snapshot_voting_power(proposal_id)
    
    def _snapshot_voting_power(self, proposal_id: str):
        """Take a snapshot of voting power at proposal creation"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return
        
        # Simplified - in production, get from ledger state
        # For now, we'll use a mock
        # This should query the ledger for token balances + reputation weights
        proposal.voting_power_snapshot = self.voting_power_cache.copy()
    
    def cast_vote(self, proposal_id: str, voter_did: str, support: bool, weight: int = 1):
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: The proposal ID
            voter_did: The voter's DID
            support: True for yes, False for no
            weight: Voting weight (usually derived from stake/reputation)
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            logging.error(f"Proposal {proposal_id} not found")
            return False
        
        if proposal.status != ProposalStatus.COMMUNITY_VOTE:
            logging.warning(f"Proposal {proposal_id} is not in voting phase")
            return False
        
        current_time = time.time()
        if current_time < proposal.voting_start or current_time > proposal.voting_end:
            logging.warning(f"Proposal {proposal_id} voting period is not active")
            return False
        
        # Check for delegation
        if voter_did in proposal.delegated_votes:
            delegate = proposal.delegated_votes[voter_did]
            logging.info(f"Vote from {voter_did} delegated to {delegate}")
            return self.cast_vote(proposal_id, delegate, support, weight)
        
        # Record vote
        if support:
            proposal.votes_for[voter_did] = proposal.votes_for.get(voter_did, 0) + weight
        else:
            proposal.votes_against[voter_did] = proposal.votes_against.get(voter_did, 0) + weight
        
        logging.info(f"Vote cast on {proposal_id} by {voter_did}: {'FOR' if support else 'AGAINST'} (weight: {weight})")
        
        # Check if voting is complete
        self._check_voting_complete(proposal_id)
        return True
    
    def _check_voting_complete(self, proposal_id: str):
        """Check if voting has ended and tally results"""
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != ProposalStatus.COMMUNITY_VOTE:
            return
        
        current_time = time.time()
        if current_time < proposal.voting_end:
            return
        
        # Tally votes
        total_for = sum(proposal.votes_for.values())
        total_against = sum(proposal.votes_against.values())
        total_votes = total_for + total_against
        
        if total_votes == 0:
            proposal.passed = False
            proposal.status = ProposalStatus.REJECTED
            logging.info(f"Proposal {proposal_id} rejected: no votes")
            return
        
        for_ratio = total_for / total_votes
        
        # Determine required threshold
        required = 0.51  # Simple majority
        
        if proposal.proposal_type == ProposalType.CONSTITUTIONAL:
            required = 0.75  # Supermajority for constitutional changes
        
        # Wisdom oracle adds weight if it strongly endorsed
        if proposal.wisdom_verdict and proposal.wisdom_verdict.confidence > 0.8:
            required *= 0.9  # Lower threshold if wisdom strongly supports
        
        passed = for_ratio >= required
        proposal.passed = passed
        proposal.status = ProposalStatus.PASSED if passed else ProposalStatus.REJECTED
        
        logging.info(f"Proposal {proposal_id} {'PASSED' if passed else 'REJECTED'} (for: {for_ratio:.2%}, required: {required:.2%})")
        
        if passed:
            self._implement_proposal(proposal_id)
    
    def _implement_proposal(self, proposal_id: str):
        """Execute a passed proposal"""
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != ProposalStatus.PASSED:
            return
        
        results = {"status": "implemented", "actions": []}
        
        # Handle different proposal types
        if proposal.proposal_type == ProposalType.PARAMETER_CHANGE:
            # Apply parameter changes
            for param, value in proposal.parameter_changes.items():
                # In production: update network config
                results["actions"].append(f"Changed {param} to {value}")
        
        elif proposal.proposal_type == ProposalType.TREASURY:
            # Transfer funds
            if proposal.recipient_did and proposal.amount:
                # In production: call ledger state
                results["actions"].append(f"Transferred {proposal.amount} to {proposal.recipient_did}")
        
        elif proposal.proposal_type == ProposalType.JUSTICE_APPEAL:
            # Handle justice appeal
            if proposal.dispute_id:
                # Trigger restorative justice review
                results["actions"].append(f"Justice appeal for dispute {proposal.dispute_id} approved")
        
        elif proposal.proposal_type == ProposalType.CULTURAL:
            # Schedule celebration
            results["actions"].append(f"Cultural event scheduled: {proposal.title}")
        
        elif proposal.proposal_type == ProposalType.WISDOM_UPDATE:
            # Update wisdom oracle (handled by oracle itself)
            results["actions"].append("Wisdom traditions updated")
        
        proposal.implementation_results = results
        proposal.implemented_at = time.time()
        proposal.status = ProposalStatus.IMPLEMENTED
        
        self.execution_history.append({
            "proposal_id": proposal_id,
            "implemented_at": proposal.implemented_at,
            "results": results
        })
        
        logging.info(f"Proposal {proposal_id} implemented successfully")
    
    def delegate_vote(self, proposal_id: str, voter_did: str, delegate_did: str):
        """Delegate voting power to another DID"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        proposal.delegated_votes[voter_did] = delegate_did
        logging.info(f"Vote delegated: {voter_did} → {delegate_did} on proposal {proposal_id}")
        return True
    
    def get_proposal_status(self, proposal_id: str) -> Dict[str, Any]:
        """Get detailed status of a proposal"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}
        
        total_for = sum(proposal.votes_for.values())
        total_against = sum(proposal.votes_against.values())
        
        return {
            "id": proposal.id,
            "title": proposal.title,
            "status": proposal.status.value,
            "type": proposal.proposal_type.value,
            "created_at": proposal.created_at,
            "voting_end": proposal.voting_end,
            "votes_for": total_for,
            "votes_against": total_against,
            "voter_count": len(proposal.votes_for) + len(proposal.votes_against),
            "wisdom_confidence": proposal.wisdom_verdict.confidence if proposal.wisdom_verdict else None,
            "wisdom_consensus": [t.value for t in proposal.wisdom_verdict.consensus_traditions] if proposal.wisdom_verdict else [],
            "wisdom_dissent": [t.value for t in proposal.wisdom_verdict.dissenting_traditions] if proposal.wisdom_verdict else [],
            "passed": proposal.passed,
            "implemented_at": proposal.implemented_at
        }
    
    def get_wisdom_for_proposal(self, proposal_id: str) -> List[Dict[str, str]]:
        """Get wisdom quotes relevant to this proposal"""
        proposal = self.proposals.get(proposal_id)
        if not proposal or not proposal.wisdom_verdict:
            return []
        
        # Get quotes from traditions that dissented (to guide amendment)
        dissenting = proposal.wisdom_verdict.dissenting_traditions
        quotes = []
        
        for tradition in dissenting:
            tradition_quotes = [q for q in self.wisdom_oracle.quotes if q.tradition == tradition]
            if tradition_quotes:
                quote = tradition_quotes[0]
                quotes.append({
                    "tradition": tradition.value,
                    "quote": quote.quote,
                    "source": quote.source,
                    "principle": quote.principle
                })
        
        return quotes[:3]  # Return top 3
