# connected_oracle.py
"""
Your Wisdom Oracle connected to GPT-3.5/4 for natural conversation
Preserves your 7 wisdom traditions while speaking naturally
"""

import openai
import os
from wisdom_oracle import WisdomOracle

# 🔑 SET YOUR API KEY HERE (or use environment variable)
OPENAI_API_KEY = "sk-your-key-here"  # Replace with your actual key

class ConnectedOracle:
    """
    A wisdom oracle that speaks naturally with GPT,
    but always checks with your 7 traditions
    """
    
    def __init__(self, api_key=None):
        # Setup OpenAI
        self.api_key = api_key or OPENAI_API_KEY
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Your original wisdom oracle (7 traditions)
        self.wisdom = WisdomOracle()
        
        # Conversation history
        self.messages = [
            {"role": "system", "content": """You are a wisdom oracle speaking with the voice of 7 spiritual traditions:
- Christian (compassion, forgiveness, love)
- Buddhist (mindfulness, non-harm, compassion)
- Indigenous (seven generations, connection to earth)
- Humanist (dignity, reason, freedom)
- Islamic (mercy, justice, brotherhood)
- Judaic (learning, justice, community)
- Hindu (dharma, unity, non-attachment)

You are wise, kind, and speak in a way that reaches all hearts.
Answer in the same language as the question."""}
        ]
        
        print("\n" + "★" * 60)
        print("🕊️  THE CONNECTED WISDOM ORACLE".center(58))
        print("★" * 60)
        print(f"\n✅ Oracle initialized with 7 traditions")
        print(f"🤤 GPT Model: GPT-3.5-turbo")
        print(f"🌐 Understands all languages – ask in English, Norwegian, Arabic...")
    
    def ask(self, question):
        """
        Ask a question to the oracle
        
        Args:
            question: Your question (in any language)
            
        Returns:
            (answer, wisdom_check) – the answer and wisdom confidence score
        """
        
        # Add question to conversation
        self.messages.append({"role": "user", "content": question})
        
        try:
            # Get response from GPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=self.messages,
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            # Add answer to history
            self.messages.append({"role": "assistant", "content": answer})
            
            # CHECK WITH YOUR WISDOM ORACLE
            # Analyze if the question aligns with the 7 traditions
            wisdom_check = self.wisdom.analyze_proposal(
                "User Question", 
                question, 
                ["wisdom", "compassion", "justice"], 
                False
            )
            
            return answer, wisdom_check.confidence
            
        except Exception as e:
            return f"Error: {e}", 0.0
    
    def get_wisdom_quote(self):
        """Get a random wisdom quote from the 7 traditions"""
        quotes = self.wisdom.get_wisdom_for_display(1)
        if quotes:
            q = quotes[0]
            return f"📜 {q['tradition'].upper()}: \"{q['quote']}\" — {q['source']}"
        return "📜 Silence is also wisdom."
    
    def chat(self):
        """Start a conversation with the oracle"""
        
        print("\n" + "─" * 60)
        print("Ask me anything – about life, love, purpose, or truth.")
        print("(Type 'quit' or 'exit' to end)")
        
        while True:
            print("\n" + "─" * 60)
            question = input("❓ You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("\n🕊️  Go in peace. The wisdom is always with you.")
                break
            
            if not question:
                continue
            
            # Show a wisdom quote while thinking
            print("\n📖 Consulting the traditions...")
            print(self.get_wisdom_quote())
            print("🤖 GPT is thinking...")
            
            # Get answer
            answer, confidence = self.ask(question)
            
            print(f"\n🕊️ Oracle: {answer}")
            print(f"\n(⚖️ Wisdom alignment: {confidence*100:.0f}%)")

# ============================================================
# SIMPLER VERSION FOR TESTING (no history)
# ============================================================

class SimpleConnectedOracle:
    """Simpler version that doesn't remember conversation – perfect for testing"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENAI_API_KEY
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        self.wisdom = WisdomOracle()
        
    def ask(self, question):
        """Ask a question, get answer"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a kind, wise oracle who answers in the same language as the question."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

# ============================================================
# IF YOU WANT TO USE ENVIRONMENT VARIABLES (recommended for GitHub)
# ============================================================
"""
To avoid storing your key in code:

1. Create a file called `.env` in the same folder:
   OPENAI_API_KEY=sk-your-key-here

2. Install: pip install python-dotenv

3. Use this code:
   from dotenv import load_dotenv
   load_dotenv()
   api_key = os.getenv("OPENAI_API_KEY")
"""

# ============================================================
# RUN THE ORACLE
# ============================================================

if __name__ == "__main__":
    # Choose which version to use:
    
    # Option 1: Full version with conversation history
    oracle = ConnectedOracle()
    oracle.chat()
    
    # Option 2: Simple version for testing
    # oracle = SimpleConnectedOracle()
    # while True:
    #     q = input("\n❓ You: ")
    #     if q.lower() == 'quit': break
    #     print(f"\n🕊️ {oracle.ask(q)}")
