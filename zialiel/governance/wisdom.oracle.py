# zialiel/governance/wisdom_oracle.py
"""
Wisdom Oracle - Multi-Traditional Ethical Analysis for Governance
Restores the spiritual core of the original 808-line vision.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tradition(Enum):
    """Wisdom traditions represented in the oracle"""
    CHRISTIAN = "christian"
    BUDDHIST = "buddhist"
    INDIGENOUS = "indigenous"
    HUMANIST = "humanist"
    ISLAMIC = "islamic"
    JUDAIC = "judaic"
    HINDU = "hindu"

@dataclass
class WisdomQuote:
    """A single wisdom quote from a tradition"""
    tradition: Tradition
    quote: str
    source: str
    principle: str  # e.g., "compassion", "justice", "stewardship"

@dataclass
class EthicalAnalysis:
    """Result of analyzing a proposal through one tradition"""
    tradition: Tradition
    score: float  # 0-100, how well proposal aligns
    reasoning: str
    concerns: List[str]
    recommendations: List[str]

@dataclass
class ProposalVerdict:
    """Final verdict from the Wisdom Oracle"""
    passes: bool
    confidence: float  # 0-1
    analyses: List[EthicalAnalysis]
    consensus_traditions: List[Tradition]
    dissenting_traditions: List[Tradition]
    suggested_amendments: List[str]

class WisdomOracle:
    """
    Multi-traditional ethical analysis engine for governance proposals.
    
    Each proposal is analyzed through multiple wisdom traditions.
    Constitutional changes require supermajority consensus across traditions.
    """
    
    def __init__(self):
        self.quotes = self._initialize_wisdom()
        self.tradition_weights = {
            Tradition.CHRISTIAN: 1.0,
            Tradition.BUDDHIST: 1.0,
            Tradition.INDIGENOUS: 1.0,
            Tradition.HUMANIST: 1.0,
            Tradition.ISLAMIC: 1.0,
            Tradition.JUDAIC: 1.0,
            Tradition.HINDU: 1.0
        }
        logging.info(f"WisdomOracle initialized with {len(self.tradition_weights)} traditions")
    
    def _initialize_wisdom(self) -> List[WisdomQuote]:
        """Seed the oracle with foundational wisdom quotes"""
        return [
            # Christian
            WisdomQuote(
                tradition=Tradition.CHRISTIAN,
                quote="Do unto others as you would have them do unto you.",
                source="Gospel of Matthew 7:12",
                principle="reciprocity"
            ),
            WisdomQuote(
                tradition=Tradition.CHRISTIAN,
                quote="The last shall be first, and the first last.",
                source="Gospel of Matthew 20:16",
                principle="humility"
            ),
            
            # Buddhist
            WisdomQuote(
                tradition=Tradition.BUDDHIST,
                quote="Hurt not others in ways that you yourself would find hurtful.",
                source="Udana-Varga 5:18",
                principle="non-harm"
            ),
            WisdomQuote(
                tradition=Tradition.BUDDHIST,
                quote="Hatred does not cease by hatred, but by love alone.",
                source="Dhammapada 1:5",
                principle="compassion"
            ),
            
            # Indigenous
            WisdomQuote(
                tradition=Tradition.INDIGENOUS,
                quote="Consider the effect on seven generations.",
                source="Haudenosaunee Confederacy",
                principle="long-term stewardship"
            ),
            WisdomQuote(
                tradition=Tradition.INDIGENOUS,
                quote="The earth does not belong to us; we belong to the earth.",
                source="Chief Seattle (attributed)",
                principle="stewardship"
            ),
            
            # Humanist
            WisdomQuote(
                tradition=Tradition.HUMANIST,
                quote="Act in such a way that you treat humanity, whether in yourself or in another, always as an end and never merely as a means.",
                source="Immanuel Kant",
                principle="dignity"
            ),
            WisdomQuote(
                tradition=Tradition.HUMANIST,
                quote="The arc of the moral universe is long, but it bends toward justice.",
                source="Martin Luther King Jr.",
                principle="justice"
            ),
            
            # Islamic
            WisdomQuote(
                tradition=Tradition.ISLAMIC,
                quote="None of you truly believes until he wishes for his brother what he wishes for himself.",
                source="Hadith 13",
                principle="brotherhood"
            ),
            WisdomQuote(
                tradition=Tradition.ISLAMIC,
                quote="Whoever kills one person, it is as if he has killed all mankind.",
                source="Quran 5:32",
                principle="sanctity of life"
            ),
            
            # Judaic
            WisdomQuote(
                tradition=Tradition.JUDAIC,
                quote="What is hateful to you, do not do to your fellow.",
                source="Talmud, Shabbat 31a",
                principle="empathy"
            ),
            WisdomQuote(
                tradition=Tradition.JUDAIC,
                quote="Justice, justice shall you pursue.",
                source="Deuteronomy 16:20",
                principle="justice"
            ),
            
            # Hindu
            WisdomQuote(
                tradition=Tradition.HINDU,
                quote="This is the sum of duty: do not do to others what would cause pain if done to you.",
                source="Mahabharata 5:1517",
                principle="dharma"
            ),
            WisdomQuote(
                tradition=Tradition.HINDU,
                quote="The self is in all beings, and all beings are in the self.",
                source="Bhagavad Gita 6:29",
                principle="unity"
            ),
        ]
    
    def analyze_proposal(self, 
                        proposal_title: str,
                        proposal_description: str,
                        affected_principles: List[str],
                        is_constitutional: bool = False) -> ProposalVerdict:
        """
        Analyze a governance proposal through all wisdom traditions.
        
        Args:
            proposal_title: Short title of proposal
            proposal_description: Full description
            affected_principles: Which principles this touches (e.g., ["justice", "stewardship"])
            is_constitutional: Whether this changes core constitution
        
        Returns:
            ProposalVerdict with analysis from all traditions
        """
        logging.info(f"Analyzing proposal: {proposal_title}")
        
        analyses = []
        for tradition in Tradition:
            analysis = self._analyze_tradition(
                tradition, 
                proposal_title,
                proposal_description,
                affected_principles
            )
            analyses.append(analysis)
        
        # Calculate consensus
        passing_traditions = [a for a in analyses if a.score >= 70]
        failing_traditions = [a for a in analyses if a.score < 70]
        
        consensus_traditions = [a.tradition for a in passing_traditions]
        dissenting_traditions = [a.tradition for a in failing_traditions]
        
        # Calculate confidence (weighted average)
        total_weight = sum(self.tradition_weights.values())
        weighted_sum = sum(a.score * self.tradition_weights[a.tradition] for a in analyses)
        confidence = weighted_sum / total_weight / 100  # 0-1 scale
        
        # Determine if proposal passes
        if is_constitutional:
            # Constitutional changes need 75% consensus across traditions
            passes = (len(passing_traditions) / len(Tradition)) >= 0.75
        else:
            # Regular proposals need simple majority
            passes = (len(passing_traditions) / len(Tradition)) >= 0.51
        
        # Generate suggested amendments from dissenting traditions
        suggested_amendments = []
        for analysis in failing_traditions:
            suggested_amendments.extend(analysis.recommendations[:2])  # Top 2 from each
        
        verdict = ProposalVerdict(
            passes=passes,
            confidence=confidence,
            analyses=analyses,
            consensus_traditions=consensus_traditions,
            dissenting_traditions=dissenting_traditions,
            suggested_amendments=list(set(suggested_amendments))[:5]  # Unique, max 5
        )
        
        logging.info(f"Analysis complete. Passes: {passes}, Confidence: {confidence:.2f}")
        return verdict
    
    def _analyze_tradition(self, 
                          tradition: Tradition,
                          title: str,
                          description: str,
                          principles: List[str]) -> EthicalAnalysis:
        """
        Analyze proposal through a single tradition.
        
        This is a simplified implementation. In production, this could use:
        - Fine-tuned LLMs per tradition
        - Rule-based ethical frameworks
        - Community voting by tradition representatives
        """
        # Base score starts at 50 (neutral)
        score = 50.0
        reasoning = []
        concerns = []
        recommendations = []
        
        # Map principles to tradition-specific values
        tradition_values = self._get_tradition_values(tradition)
        
        # Score based on principle alignment
        for principle in principles:
            if principle in tradition_values["supports"]:
                score += 10
                reasoning.append(f"Principle '{principle}' aligns with {tradition.value} values")
            elif principle in tradition_values["warns"]:
                score -= 15
                concerns.append(f"Principle '{principle}' raises concerns in {tradition.value} tradition")
                recommendations.append(f"Consider how to address {principle} in light of {tradition.value} wisdom")
        
        # Check for key terms in description
        description_lower = description.lower()
        
        # Positive indicators
        for term in tradition_values["positive_terms"]:
            if term in description_lower:
                score += 5
                reasoning.append(f"Contains '{term}' which resonates with {tradition.value}")
        
        # Negative indicators
        for term in tradition_values["negative_terms"]:
            if term in description_lower:
                score -= 10
                concerns.append(f"Contains '{term}' which may conflict with {tradition.value}")
                recommendations.append(f"Reframe language around '{term}' to better align with {tradition.value} wisdom")
        
        # Clamp score to 0-100
        score = max(0, min(100, score))
        
        # Add tradition-specific wisdom quote
        tradition_quotes = [q for q in self.quotes if q.tradition == tradition]
        if tradition_quotes:
            quote = tradition_quotes[0]  # Just use first for demo
            reasoning.append(f"Wisdom reminder: '{quote.quote}' — {quote.source}")
        
        return EthicalAnalysis(
            tradition=tradition,
            score=score,
            reasoning=" ".join(reasoning[:3]),  # Summarize
            concerns=concerns[:3],
            recommendations=recommendations[:3]
        )
    
    def _get_tradition_values(self, tradition: Tradition) -> Dict[str, Any]:
        """Get value mappings for a tradition"""
        values = {
            Tradition.CHRISTIAN: {
                "supports": ["compassion", "forgiveness", "stewardship", "justice", "love"],
                "warns": ["greed", "exploitation", "oppression"],
                "positive_terms": ["mercy", "grace", "serve", "community", "poor"],
                "negative_terms": ["dominate", "conquer", "accumulate", "exclude"]
            },
            Tradition.BUDDHIST: {
                "supports": ["non-harm", "compassion", "mindfulness", "detachment"],
                "warns": ["attachment", "craving", "harm"],
                "positive_terms": ["suffering", "release", "awakening", "middle"],
                "negative_terms": ["cling", "grasp", "desire", "violence"]
            },
            Tradition.INDIGENOUS: {
                "supports": ["stewardship", "community", "ancestors", "seven generations"],
                "warns": ["exploitation", "disrespect", "short-term"],
                "positive_terms": ["land", "sacred", "balance", "circle", "gift"],
                "negative_terms": ["take", "own", "dominate", "extract"]
            },
            Tradition.HUMANIST: {
                "supports": ["dignity", "reason", "rights", "autonomy", "progress"],
                "warns": ["dogma", "oppression", "irrational"],
                "positive_terms": ["freedom", "choice", "education", "evidence"],
                "negative_terms": ["blind", "obey", "authority", "suppress"]
            },
            Tradition.ISLAMIC: {
                "supports": ["justice", "brotherhood", "mercy", "charity"],
                "warns": ["injustice", "oppression", "waste"],
                "positive_terms": ["peace", "compassion", "balance", "knowledge"],
                "negative_terms": ["corruption", "excess", "harm", "injustice"]
            },
            Tradition.JUDAIC: {
                "supports": ["justice", "repair", "dignity", "community"],
                "warns": ["idolatry", "oppression", "injustice"],
                "positive_terms": ["pursue", "heal", "remember", "holy"],
                "negative_terms": ["false", "exploit", "forget", "ignore"]
            },
            Tradition.HINDU: {
                "supports": ["dharma", "unity", "non-harm", "detachment"],
                "warns": ["adharma", "illusion", "attachment"],
                "positive_terms": ["sacred", "duty", "path", "liberation"],
                "negative_terms": ["bind", "delude", "harm", "separate"]
            }
        }
        return values.get(tradition, {"supports": [], "warns": [], "positive_terms": [], "negative_terms": []})
    
    def get_wisdom_for_display(self, count: int = 3) -> List[Dict[str, str]]:
        """Get random wisdom quotes for UI display"""
        import random
        selected = random.sample(self.quotes, min(count, len(self.quotes)))
        return [
            {
                "tradition": q.tradition.value,
                "quote": q.quote,
                "source": q.source,
                "principle": q.principle
            }
            for q in selected
        ]
