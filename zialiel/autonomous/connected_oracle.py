#!/usr/bin/env python3
# connected_oracle.py – AI Oracle with Grok support and .env configuration

import openai
import os
import sys
import logging
from dotenv import load_dotenv
from wisdom_oracle import WisdomOracle

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ConnectedOracle")

class ConnectedOracle:
    """
    A wisdom oracle that speaks naturally with AI (Grok or GPT),
    but always checks with your 7 wisdom traditions.
    
    Features:
    - Uses Grok (xAI) or GPT-4o based on .env configuration
    - Validates both questions and answers against Wisdom Oracle
    - Maintains conversation history
    - Responds in the same language as the question
    - Integrates with your existing .env file
    """
    
    def __init__(self):
        """Initialize the Connected Oracle with AI model and wisdom traditions"""
        
        # Determine which AI model to use from .env
        self.model = os.getenv("ORACLE_MODEL", "grok-4")
        self.use_grok = "grok" in self.model.lower()
        
        # Configure AI client
        if self.use_grok:
            # xAI/Grok configuration
            self.api_key = os.getenv("XAI_API_KEY")
            if not self.api_key:
                logger.error("XAI_API_KEY missing in .env file")
                sys.exit(1)
            
            openai.api_key = self.api_key
            openai.base_url = "https://api.x.ai/v1/"
            logger.info(f"Using Grok model: {self.model}")
        else:
            # OpenAI configuration
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.error("OPENAI_API_KEY missing in .env file")
                sys.exit(1)
            
            openai.api_key = self.api_key
            logger.info(f"Using OpenAI model: {self.model}")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Your original wisdom oracle (7 traditions)
        self.wisdom = WisdomOracle()
        
        # Conversation history with system prompt embedding the 7 traditions
        self.messages = [
            {"role": "system", "content": """You are a wisdom oracle speaking with the voice of 7 spiritual traditions:

- Christian: compassion, forgiveness, love, stewardship
- Buddhist: mindfulness, non-harm, compassion, awareness
- Indigenous: seven generations, connection to earth, gratitude
- Humanist: dignity, reason, freedom, ethical action
- Islamic: mercy, justice, brotherhood, knowledge
- Judaic: learning, justice, community, repair
- Hindu: dharma, unity, non-attachment, service

You are wise, kind, and speak in a way that reaches all hearts.
Answer in the same language as the question.
Always consider the effect on seven generations.
Be humble – admit when you don't know something."""}
        ]
        
        print("\n" + "★" * 60)
        print("🕊️  THE CONNECTED WISDOM ORACLE".center(58))
        print("★" * 60)
        print(f"\n✅ Oracle initialized with 7 traditions")
        print(f"🤖 AI Model: {self.model}")
        print(f"🌐 Understands all languages – ask in English, Norwegian, Arabic...")
        print(f"💾 Conversation memory: Active")
    
    def ask(self, question):
        """
        Ask a question to the oracle
        
        Args:
            question: Your question (in any language)
            
        Returns:
            tuple: (answer, wisdom_confidence, question_confidence)
        """
        
        # STEP 1: Check if the question itself aligns with wisdom
        question_check = self.wisdom.analyze_proposal(
            "User Question", 
            question, 
            ["wisdom", "compassion", "justice", "truth"], 
            False
        )
        
        # If question is completely against wisdom, warn but still try to answer
        if question_check.confidence < 0.3:
            logger.warning(f"Question has low wisdom alignment: {question_check.confidence:.1%}")
        
        # Add question to conversation
        self.messages.append({"role": "user", "content": question})
        
        try:
            # Get response from AI
            logger.info(f"Getting response from {self.model}...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Add answer to history
            self.messages.append({"role": "assistant", "content": answer})
            
            # STEP 2: Check if the ANSWER aligns with wisdom
            answer_check = self.wisdom.analyze_proposal(
                "AI Response", 
                f"Question: {question}\n\nAnswer: {answer}", 
                ["wisdom", "compassion", "justice", "truth"], 
                False
            )
            
            logger.info(f"Wisdom alignment - Question: {question_check.confidence:.1%}, Answer: {answer_check.confidence:.1%}")
            
            return answer, answer_check.confidence, question_check.confidence
            
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return f"I encountered an error: {e}", 0.0, 0.0
    
    def get_wisdom_quote(self):
        """Get a random wisdom quote from the 7 traditions"""
        quotes = self.wisdom.get_wisdom_for_display(1)
        if quotes and len(quotes) > 0:
            q = quotes[0]
            return f"📜 {q['tradition'].upper()}: \"{q['quote']}\" — {q['source']}"
        return "📜 Silence is also wisdom."
    
    def reset_conversation(self):
        """Reset conversation history but keep system prompt"""
        system = self.messages[0]
        self.messages = [system]
        print("🔄 Conversation reset.")
    
    def chat(self):
        """Start an interactive conversation with the oracle"""
        
        print("\n" + "─" * 60)
        print("Ask me anything – about life, love, purpose, or truth.")
        print("Commands: 'quit' to exit, 'reset' to clear history, 'wisdom' for new quote")
        
        while True:
            print("\n" + "─" * 60)
            question = input("❓ You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("\n🕊️  Go in peace. The wisdom is always with you.")
                print("   'The arc of the moral universe is long, but it bends toward justice.' — MLK Jr.")
                break
            
            if question.lower() == 'reset':
                self.reset_conversation()
                continue
            
            if question.lower() == 'wisdom':
                print("\n" + self.get_wisdom_quote())
                continue
            
            if not question:
                continue
            
            # Show a wisdom quote while thinking
            print("\n📖 Consulting the traditions...")
            print(self.get_wisdom_quote())
            print("🤖 Thinking...")
            
            # Get answer
            answer, answer_conf, question_conf = self.ask(question)
            
            print(f"\n🕊️ Oracle: {answer}")
            print(f"\n(⚖️ Wisdom alignment: Question: {question_conf*100:.0f}%, Answer: {answer_conf*100:.0f}%)")
            
            # Warn if answer has low alignment
            if answer_conf < 0.6:
                print("⚠️  Note: This answer had lower wisdom alignment. Consider asking differently.")


# ============================================================
# SIMPLER VERSION FOR TESTING (no conversation history)
# ============================================================

class SimpleConnectedOracle:
    """Simpler version without conversation memory – perfect for quick testing"""
    
    def __init__(self):
        # Determine which AI model to use from .env
        self.model = os.getenv("ORACLE_MODEL", "grok-4")
        self.use_grok = "grok" in self.model.lower()
        
        if self.use_grok:
            self.api_key = os.getenv("XAI_API_KEY")
            openai.api_key = self.api_key
            openai.base_url = "https://api.x.ai/v1/"
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
            openai.api_key = self.api_key
        
        if not self.api_key:
            print("❌ Missing API key in .env file")
            sys.exit(1)
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.wisdom = WisdomOracle()
    
    def ask(self, question):
        """Ask a question, get answer (no memory)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a kind, wise oracle who answers in the same language as the question. You embody 7 wisdom traditions."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content
            
            # Check with wisdom oracle
            check = self.wisdom.analyze_proposal(
                "Simple Query", 
                f"Q: {question}\nA: {answer}", 
                ["wisdom", "compassion"], 
                False
            )
            
            return answer, check.confidence
            
        except Exception as e:
            return f"Error: {e}", 0.0


# ============================================================
# RUN THE ORACLE
# ============================================================

if __name__ == "__main__":
    print("\n🕊️  CONNECTED WISDOM ORACLE")
    print("=" * 60)
    print("Choose mode:")
    print("1. Full version (with conversation history)")
    print("2. Simple version (no memory, quick testing)")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == "2":
        # Simple version
        oracle = SimpleConnectedOracle()
        print("\n" + "─" * 60)
        print("Simple mode – no conversation memory. Type 'quit' to exit.")
        
        while True:
            q = input("\n❓ You: ").strip()
            if q.lower() in ['quit', 'exit']:
                print("\n🕊️  Peace be with you.")
                break
            if not q:
                continue
            
            answer, conf = oracle.ask(q)
            print(f"\n🕊️ Oracle: {answer}")
            print(f"(⚖️ Wisdom: {conf*100:.0f}%)")
    
    else:
        # Full version (default)
        oracle = ConnectedOracle()
        oracle.chat()
