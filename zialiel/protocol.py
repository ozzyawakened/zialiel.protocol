
import json
import time
import random
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from .crypto_core.identity import DID, Reputation
from .crypto_core.transactions import Transaction, DAG
from .crypto_core.signature import SignatureScheme
from .economics.fees import FeeDistributor
from .economics.ubi import UBIDistributor
from .governance.justice import Dispute, DisputeStatus, RestorativeJustice
from .ledger.ledger import Ledger


# -------------------------------------
# 7. ENVIRONMENTAL MECHANISMS
# -------------------------------------

class EnvironmentalStewardship:
    # ✅ BUG FIX: Pass the entire FeeDistributor instance
    def __init__(self, fee_distributor: FeeDistributor):
        self.fee_distributor = fee_distributor
        self.green_validators = set()  # DIDs with renewable energy proof
        self.carbon_projects = []  # Verified carbon removal projects
    
    def register_green_validator(self, did: str, renewable_proof: str):
        """Register validator using renewable energy"""
        if len(renewable_proof) > 10:  # Simplified verification
            self.green_validators.add(did)
            return True
        return False
    
    def calculate_validator_reward(self, did: str, base_reward: float) -> float:
        """Bonus for green validators"""
        if did in self.green_validators:
            return base_reward * 1.1  # 10% bonus
        return base_reward
    
    def fund_carbon_project(self, project_id: str, amount: float, current_time_func):
        """Fund verified carbon removal project"""
        if amount <= self.fee_distributor.carbon_fund:
            self.fee_distributor.carbon_fund -= amount
            self.carbon_projects.append({
                'project_id': project_id,
                'funded_amount': amount,
                'timestamp': current_time_func()
            })
            return True
        return False

# -------------------------------------
# 8. ACCESSIBILITY LAYER
# -------------------------------------

class AccessibilityLayer:
    """Interface for low-resource users"""
    
    @staticmethod
    def create_light_client_transaction(sender_did: str, recipient_did: str, 
                                        amount: float, private_key: str, current_time_func) -> dict:
        """Create transaction optimized for light clients"""
        tx_data = {
            'sender': sender_did,
            'recipient': recipient_did,
            'amount': amount,
            'timestamp': current_time_func(),
            'light_client': True
        }
        message = json.dumps(tx_data)
        signature = SignatureScheme.sign(private_key, message)
        tx_data['signature'] = signature
        return tx_data
    
    @staticmethod
    def voice_transaction(sender_did: str, audio_command: str):
        """Process voice-initiated transaction (simplified)"""
        # In production: NLP processing, IVR integration
        if "send" in audio_command and "to" in audio_command:
            # Parse: "send 10 to did:example:123"
            return True
        return False
    
    @staticmethod
    def offline_transaction_builder(tx_data: dict, peer_did: str):
        """Build transaction for later broadcast when online"""
        # Store in local storage, propagate via mesh when available
        return {"offline": True, "data": tx_data, "target": peer_did}

# -------------------------------------
# 9. WISDOM IN GOVERNANCE
# -------------------------------------

class ConstitutionalPrinciple(Enum):
    CENSORSHIP_RESISTANCE = 1
    PRIVATE_KEY_SOVEREIGNTY = 2
    NON_DISCRIMINATION = 3
    RESTORATIVE_JUSTICE = 4
    STEWARDSHIP_OF_CREATION = 5

@dataclass
class Proposal:
    id: str
    title: str
    description: str
    proposer_did: str
    created_at: int
    deliberation_end: int
    voting_start: int
    voting_end: int
    affected_parameters: List[str]
    constitutional_impact: List[ConstitutionalPrinciple]
    votes_for: float = 0.0
    votes_against: float = 0.0
    delegated_votes: Dict = field(default_factory=dict)
    status: str = "deliberation"  # deliberation, voting, passed, failed

class WisdomGovernance:
    def __init__(self):
        self.proposals = {}
        self.constitution = {
            ConstitutionalPrinciple.CENSORSHIP_RESISTANCE: {
                'threshold': 0.75,  # 75% supermajority to change
                'description': "No central authority shall freeze wallets or censor transactions"
            },
            ConstitutionalPrinciple.PRIVATE_KEY_SOVEREIGNTY: {
                'threshold': 0.75,
                'description': "Users alone control their private keys and assets"
            },
            ConstitutionalPrinciple.NON_DISCRIMINATION: {
                'threshold': 0.66,
                'description': "Protocol shall not discriminate based on identity"
            },
            ConstitutionalPrinciple.RESTORATIVE_JUSTICE: {
                'threshold': 0.66,
                'description': "Justice shall include paths for restoration"
            },
            ConstitutionalPrinciple.STEWARDSHIP_OF_CREATION: {
                'threshold': 0.66,
                'description': "Network shall care for the environment"
            }
        }
        self.wisdom_oracles = []  # Quotes from diverse traditions
    
    def add_wisdom(self, tradition: str, quote: str, source: str):
        """Add wisdom quote to governance interface"""
        self.wisdom_oracles.append({
            'tradition': tradition,
            'quote': quote,
            'source': source
        })
    
    def create_proposal(self, proposal: Proposal):
        """Create new governance proposal with deliberation period"""
        if proposal.deliberation_end - proposal.created_at < 604800:  # Min 7 days
            return False
        
        # Check constitutional impact
        for principle in proposal.constitutional_impact:
            if principle in self.constitution:
                # Require higher threshold for constitutional changes
                proposal.requires_supermajority = True
        
        self.proposals[proposal.id] = proposal
        return proposal.id
    
    def vote(self, proposal_id: str, voter_did: str, weight: float, support: bool):
        """Vote on proposal (with optional delegation)"""
        proposal = self.proposals.get(proposal_id)
        if not proposal or proposal.status != "voting":
            return False
        
        # Check delegation
        if proposal.delegated_votes and voter_did in proposal.delegated_votes:
            delegate = proposal.delegated_votes[voter_did]
            # Delegate votes instead
            return self.vote(proposal_id, delegate, weight, support)
        
        if support:
            proposal.votes_for += weight
        else:
            proposal.votes_against += weight
        
        return True
    
    def tally_proposal(self, proposal_id: str, current_time_func) -> bool:
        """Tally votes and determine outcome"""
        proposal = self.proposals.get(proposal_id)
        if not proposal or current_time_func() < proposal.voting_end:
            return False
        
        total_votes = proposal.votes_for + proposal.votes_against
        if total_votes == 0:
            proposal.status = "failed"
            return False
        
        support_ratio = proposal.votes_for / total_votes
        
        # Determine required threshold
        threshold = 0.5  # Default 50%
        if hasattr(proposal, 'requires_supermajority') and proposal.requires_supermajority:
            # Find the highest threshold required by the affected principles
            max_threshold = 0
            for principle in proposal.constitutional_impact:
                if self.constitution.get(principle, {}).get('threshold', 0) > max_threshold:
                    max_threshold = self.constitution[principle]['threshold']
            threshold = max_threshold

        if support_ratio >= threshold:
            proposal.status = "passed"
            # In a real system, this would trigger the parameter changes
            return True
        else:
            proposal.status = "failed"
            return False

# ------------------------------------
# 10. GRATITUDE & CELEBRATION
# ------------------------------------

class GratitudeMechanism:
    def __init__(self, fee_distributor: FeeDistributor, current_time_func):
        self.fee_distributor = fee_distributor
        self.current_time = current_time_func
        self.gratitude_log = []

    def send_gratitude(self, from_did: str, to_did: str, amount: float):
        if amount <= self.fee_distributor.gratitude_fund:
            self.fee_distributor.gratitude_fund -= amount
            # This amount would be transferred to `to_did` via a transaction
            self.gratitude_log.append({
                "from": from_did,
                "to": to_did,
                "amount": amount,
                "timestamp": self.current_time()
            })
            print(f"💖 Gratitude sent from {from_did} to {to_did} for {amount} coins!")
            return True
        return False

# ------------------------------------
# 11. MAIN PROTOCOL & SIMULATION
# ------------------------------------
class CovenantProtocol:
    """Represents a single node in the Zialiel network."""
    def __init__(self, did: str):
        self.did = did # Each node has a unique identifier
        self.crypto_core = DAG()
        self.ledger = Ledger()
        self.reputation = Reputation(did)

        # System components that react to the ledger and core
        self.fees = FeeDistributor()
        self.ubi = UBIDistributor(self.fees)
        self.justice = RestorativeJustice()
        self.governance = WisdomGovernance()
        self.stewardship = EnvironmentalStewardship(self.fees)
        self.gratitude = GratitudeMechanism(self.fees, self.current_time)
        self.accessibility = AccessibilityLayer()
    
    def current_time(self):
        return int(time.time())

    def create_transaction(self, recipient_did: str, amount: float, fee: float, private_key: bytes, parent_transactions: List[str]):
        tx_id = str(uuid.uuid4())
        # The signature should cover the essential, immutable parts of the transaction.
        message_to_sign = f"{tx_id}{self.did}{recipient_did}{amount}{fee}".encode('utf-8')
        signature = SignatureScheme.sign(private_key, message_to_sign)
        
        tx = Transaction(
            id=tx_id,
            sender_did=self.did,
            recipient_did=recipient_did,
            amount=amount,
            fee=fee,
            fee_split={}, # Simplified for now
            signature=signature,
            timestamp=self.current_time(),
            parent_transactions=parent_transactions,
            collateral=amount * 0.01, # Simplified
        )
        return tx

    def submit_transaction(self, tx: Transaction):
        """Submits a transaction to this node's view of the DAG."""
        return self.crypto_core.add_transaction(tx)

    def run_consensus_round(self, all_nodes: List['CovenantProtocol']):
        """Runs one round of consensus from this node's perspective."""
        self.crypto_core.run_consensus_round(all_nodes)
        
        # After consensus, check for newly finalized transactions
        finalized_txs = self.get_newly_finalized_transactions()
        for tx in finalized_txs:
            self.apply_to_ledger_and_distribute_fees(tx)

    def get_newly_finalized_transactions(self) -> List[Transaction]:
        """ Returns transactions that are finalized but not yet applied to this node's ledger."""
        finalized = []
        for tx in self.crypto_core.transactions.values():
            # Check if finalized in the DAG and not yet recorded in the ledger
            # A simple way to check if recorded is to see if the sender's balance was debited.
            # This is a simplification; a real ledger would track transaction IDs.
            if tx.finalized and not self.ledger.has_transaction(tx.id):
                 finalized.append(tx)
        return finalized

    def apply_to_ledger_and_distribute_fees(self, tx: Transaction):
        """Applies a finalized transaction to the ledger and distributes fees."""
        if self.ledger.apply_transaction(tx):
            self.fees.distribute(tx)
            print(f"Node {self.did}: Applied transaction {tx.id} to ledger.")

# --- Simulation ---
def run_simulation():
    print("--- Zialiel Consensus Simulation ---")
    
    # 1. Create a network of validator nodes
    num_validators = 20
    # Use more realistic Avalanche parameters for a network of 20
    # k (sample size) should be smaller than num_validators
    k_param = 5 
    alpha_param = 3 # Quorum size
    beta_param = 5 # Consecutive successes
    
    validators = [CovenantProtocol(did=f"validator_{i}") for i in range(num_validators)]
    for v in validators:
        v.crypto_core.k = k_param
        v.crypto_core.alpha = alpha_param
        v.crypto_core.beta = beta_param

    # Create some user accounts with keys and initial balances
    # NOTE: In this simulation, the public key (pk) is used as the DID address.
    pk_alice, sk_alice = SignatureScheme.generate_keys()
    pk_bob, sk_bob = SignatureScheme.generate_keys()
    pk_charlie, sk_charlie = SignatureScheme.generate_keys()
    
    # Give Alice an initial balance on all ledgers for the simulation
    for validator in validators:
        validator.ledger.balances[pk_alice] = 1000.0

    print(f"Network created with {num_validators} validators (k={k_param}, α={alpha_param}, β={beta_param}).")
    print(f"Alice's initial balance: {validators[0].ledger.get_balance(pk_alice)}\n")

    # 2. Create conflicting transactions (a double spend)
    # Alice tries to send 50 coins to Bob and 50 coins to Charlie
    
    # For a DAG, transactions should reference parents. We'll start with no parents.
    initial_tips = list(validators[0].crypto_core.tips)
    
    # We need to use the validator's own DID and keys to create transactions
    # Let's assume validator_0 is acting on behalf of Alice
    alice_node = validators[0]
    alice_node.did = pk_alice # Assign Alice's public key as the node's DID

    tx1 = alice_node.create_transaction(
        recipient_did=pk_bob,
        amount=50.0,
        fee=1.0,
        private_key=sk_alice,
        parent_transactions=initial_tips
    )
    tx1.id = "tx_to_bob" # Force ID for clarity

    tx2 = alice_node.create_transaction(
        recipient_did=pk_charlie,
        amount=50.0,
        fee=1.0,
        private_key=sk_alice,
        parent_transactions=initial_tips
    )
    tx2.id = "tx_to_charlie" # Force ID for clarity

    print("Conflicting transactions created:")
    print(f"  - {tx1.id}: Alice -> 50 to Bob")
    print(f"  - {tx2.id}: Alice -> 50 to Charlie\n")

    # 3. Submit transactions to different nodes to create a split view
    # Half the network sees tx1 first, the other half sees tx2 first
    for i, validator in enumerate(validators):
        # All nodes should be aware of both transactions to resolve the conflict
        validator.submit_transaction(tx1)
        validator.submit_transaction(tx2)
        
        # Set their initial preference based on which one they "saw" first
        if i < num_validators / 2:
            validator.crypto_core.preference = tx1.id
        else:
            validator.crypto_core.preference = tx2.id
            
    print("Transactions submitted to all nodes, creating an initial preference split.\n")

    # 4. Run consensus rounds
    num_rounds = 30 # Increased rounds for better chance of finality
    print(f"--- Running up to {num_rounds} consensus rounds ---")
    finalized_tx_id = None
    for r in range(num_rounds):
        print(f"\n--- Round {r+1} ---")
        
        # In each round, every validator queries the network
        for validator_to_run in validators:
            validator_to_run.run_consensus_round(validators)

        # Check if any transaction has been finalized across the network
        # We only need one node to report finality, as all honest nodes will agree
        for tx in alice_node.crypto_core.transactions.values():
            if tx.finalized:
                finalized_tx_id = tx.id
                break
        if finalized_tx_id:
            print(f"\n🎉 Consensus reached! Transaction {finalized_tx_id} has been finalized.")
            break

    # 5. Apply final transactions to all ledgers if not already done
    if finalized_tx_id:
        final_tx_obj = alice_node.crypto_core.transactions[finalized_tx_id]
        for v in validators:
             v.apply_to_ledger_and_distribute_fees(final_tx_obj)

    # 6. Verify final state
    print("\n--- Final State ---")
    
    if not finalized_tx_id:
        print("Consensus not reached within the round limit.")
    else:
        # All nodes should have the same ledger balance in the end
        final_balance_alice = validators[0].ledger.get_balance(pk_alice)
        final_balance_bob = validators[0].ledger.get_balance(pk_bob)
        final_balance_charlie = validators[0].ledger.get_balance(pk_charlie)

        print(f"Final Balances:")
        print(f"  - Alice: {final_balance_alice:.2f}")
        print(f"  - Bob: {final_balance_bob:.2f}")
        print(f"  - Charlie: {final_balance_charlie:.2f}")

        # Verify all nodes agree
        all_agree = True
        for v in validators[1:]:
            if round(v.ledger.get_balance(pk_alice), 2) != round(final_balance_alice, 2):
                all_agree = False
                print(f"Disagreement found at {v.did}: Alice balance is {v.ledger.get_balance(pk_alice)}")
                break
        print(f"All nodes in agreement on final balances: {all_agree}")

if __name__ == "__main__":
    run_simulation()
