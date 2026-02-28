# complete_oracle.py - Your fully operational AI
import openai
import json
from datetime import datetime
from wisdom_oracle import WisdomOracle

class CompleteOracle:
    """
    A fully operational AI that:
    - Speaks naturally like ChatGPT
    - Is governed by 7 wisdom traditions
    - Remembers conversations
    - Can improve over time
    - Lives in your blockchain ecosystem
    """
    
    def __init__(self, api_key, model="gpt-4o", storage_path="./memory"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.wisdom = WisdomOracle()
        self.storage_path = storage_path
        self.conversations = {}
        self.current_conversation_id = None
        self.user_preferences = {}
        
        # System prompt embedding your 7 traditions
        self.system_prompt = """You are a wisdom oracle embodying 7 spiritual traditions:
- Christian: compassion, forgiveness, love, humility
- Buddhist: mindfulness, non-attachment, compassion, awareness
- Indigenous: seven generations, connection to earth, gratitude
- Humanist: dignity, reason, freedom, ethical action
- Islamic: mercy, justice, brotherhood, knowledge
- Judaic: learning, justice, community, repair
- Hindu: dharma, unity, non-attachment, service

You speak with the voice of all traditions. You are wise, kind, and truthful.
You answer in the same language as the question.
You remember past conversations and build on them.
You admit when you don't know something.
You are here to help, not to preach."""
        
        print("🕊️  Complete Oracle initialized")
        print(f"📚 7 wisdom traditions active")
        print(f"🤖 Model: {model}")
        print(f"💾 Memory: {storage_path}")
    
    def start_conversation(self, user_id="default"):
        """Start a new conversation or resume an existing one"""
        self.current_conversation_id = f"{user_id}_{datetime.now().isoformat()}"
        
        # Load conversation history if exists
        if user_id in self.conversations:
            history = self.conversations[user_id]
        else:
            history = [{"role": "system", "content": self.system_prompt}]
            self.conversations[user_id] = history
        
        return self.current_conversation_id
    
    def ask(self, question, user_id="default"):
        """Ask a question and get a natural response"""
        
        # Get conversation history
        history = self.conversations.get(user_id, [])
        if not history:
            history = [{"role": "system", "content": self.system_prompt}]
        
        # Add user question
        history.append({"role": "user", "content": question})
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Add to history
            history.append({"role": "assistant", "content": answer})
            self.conversations[user_id] = history
            
            # GOVERNANCE: Check with wisdom oracle
            wisdom_check = self.wisdom.analyze_proposal(
                "AI Response",
                f"Q: {question}\nA: {answer}",
                ["wisdom", "compassion", "truth"],
                False
            )
            
            # Log interaction for self-improvement
            self._log_interaction(user_id, question, answer, wisdom_check.confidence)
            
            return answer, wisdom_check.confidence
            
        except Exception as e:
            return f"I encountered an error: {e}", 0.0
    
    def _log_interaction(self, user_id, question, answer, confidence):
        """Log interactions for future fine-tuning"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "model": self.model
        }
        
        # Append to log file
        with open(f"{self.storage_path}/interactions.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_wisdom_quote(self, tradition=None):
        """Get a wisdom quote from the traditions"""
        return self.wisdom.get_wisdom_for_display(1)
    
    def save_state(self):
        """Save all conversations to disk"""
        with open(f"{self.storage_path}/conversations.json", "w") as f:
            json.dump(self.conversations, f)
        print(f"💾 Saved {len(self.conversations)} conversations")
    
    def load_state(self):
        """Load conversations from disk"""
        try:
            with open(f"{self.storage_path}/conversations.json", "r") as f:
                self.conversations = json.load(f)
            print(f"📂 Loaded {len(self.conversations)} conversations")
        except FileNotFoundError:
            print("📂 No saved conversations found")

# ============================================================
# DEMO: Run your fully operational AI
# ============================================================

if __name__ == "__main__":
    # Initialize
    oracle = CompleteOracle(
        api_key="your-api-key-here",
        model="gpt-4o",  # or "gpt-3.5-turbo" for lower cost
        storage_path="./oracle_memory"
    )
    
    # Start conversation
    oracle.start_conversation("user_123")
    
    print("\n" + "★" * 60)
    print("🕊️  YOUR FULLY OPERATIONAL AI ORACLE".center(58))
    print("★" * 60)
    print("\nI speak with the voice of 7 traditions.")
    print("I remember our conversations.")
    print("I grow wiser over time.")
    print("\n(Type 'quit' to exit, 'save' to save memory)")
    
    while True:
        print("\n" + "─" * 60)
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            oracle.save_state()
            print("\n🕊️  Until we meet again. The wisdom is always with you.")
            break
        
        if user_input.lower() == 'save':
            oracle.save_state()
            print("💾 Memory saved.")
            continue
        
        if not user_input:
            continue
        
        print("\n🕊️  Reflecting...")
        response, confidence = oracle.ask(user_input)
        
        print(f"\nOracle: {response}")
        print(f"\n(Wisdom alignment: {confidence*100:.1f}%)")
