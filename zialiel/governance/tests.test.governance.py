# zialiel/tests/test_governance.py
"""
Test the integrated governance system with Wisdom Oracle.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from governance.wisdom_oracle import WisdomOracle
from governance.justice import RestorativeJustice
from governance.proposals import GovernanceEngine, ProposalType
import time

def test_wisdom_integration():
    """Test the full governance flow with Wisdom Oracle"""
    print("\n🧠 TESTING WISDOM ORACLE INTEGRATION")
    print("=" * 50)
    
    # Initialize components
    oracle = WisdomOracle()
    justice = RestorativeJustice()
    governance = GovernanceEngine(oracle, justice)
    
    # Display some wisdom
    print("\n📜 Wisdom from the ages:")
    for w in oracle.get_wisdom_for_display(3):
        print(f"  • {w['tradition'].upper()}: \"{w['quote']}\" — {w['source']}")
    
    # Create a proposal
    print("\n📝 Creating test proposal...")
    prop_id = governance.create_proposal(
        title="Increase UBI distribution to 200 units per cycle",
        description="This proposal would raise the Universal Basic Income from 100 to 200 units per distribution cycle, ensuring greater economic security for all verified humans.",
        proposer_did="did:zialiel:alice",
        proposal_type=ProposalType.PARAMETER_CHANGE,
        parameter_changes={"ubi_amount": 200}
    )
    
    # Check wisdom verdict
    print(f"\n⚖️ Wisdom Oracle Analysis for {prop_id}:")
    status = governance.get_proposal_status(prop_id)
    print(f"  Confidence: {status['wisdom_confidence']:.2%}")
    print(f"  Consensus traditions: {', '.join(status['wisdom_consensus'])}")
    if status['wisdom_dissent']:
        print(f"  Dissenting traditions: {', '.join(status['wisdom_dissent'])}")
    
    # Cast some test votes
    print("\n🗳️ Casting test votes...")
    governance.cast_vote(prop_id, "did:zialiel:bob", True, weight=100)
    governance.cast_vote(prop_id, "did:zialiel:carol", False, weight=50)
    governance.cast_vote(prop_id, "did:zialiel:david", True, weight=75)
    
    # Simulate time passing (in production, this would be real time)
    # For test, we'll manually trigger voting completion
    proposal = governance.proposals[prop_id]
    proposal.voting_end = time.time() - 1  # Set to past
    governance._check_voting_complete(prop_id)
    
    # Check final status
    print(f"\n✅ Final Status:")
    final = governance.get_proposal_status(prop_id)
    print(f"  Passed: {final['passed']}")
    print(f"  Votes For: {final['votes_for']}")
    print(f"  Votes Against: {final['votes_against']}")
    print(f"  Status: {final['status']}")
    
    print("\n✨ Test complete! Wisdom Oracle is successfully integrated.")
    return True

if __name__ == "__main__":
    test_wisdom_integration()
