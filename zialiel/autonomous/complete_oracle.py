#!/usr/bin/env python3
# complete_oracle.py - Fully integrated AI with 7 wisdom traditions and blockchain

import openai
from web3 import Web3
import json
from datetime import datetime
from wisdom_oracle import WisdomOracle
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("oracle.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CompleteOracle")

class CompleteOracle:
    """
    A fully operational AI that:
    - Speaks naturally like ChatGPT
    - Is governed by 7 wisdom traditions
    - Remembers conversations
    - Can improve over time
    - Lives in your blockchain ecosystem
    - Uses Grok (xAI) or GPT-4o
    """
    
    def __init__(self, storage_path="./oracle_memory"):
        """
        Initialize the Complete Oracle with wisdom traditions and AI model.
        
        Args:
            storage_path: Directory for saving conversations and logs
        """
        # Choose model from environment (grok-4 or gpt-4o)
        self.model = os.getenv("ORACLE_MODEL", "grok-4")
        self.use_grok = "grok" in self.model.lower()
        
        # Configure AI
        if self.use_grok:
            # xAI/Grok configuration
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                logger.error("XAI_API_KEY missing in .env file")
                sys.exit(1)
            openai.api_key = api_key
            openai.base_url = "https://api.x.ai/v1/"
            logger.info(f"Using Grok model: {self.model}")
        else:
            # OpenAI configuration
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY missing in .env file")
                sys.exit(1)
            openai.api_key = api_key
            logger.info(f"Using OpenAI model: {self.model}")
        
        self.client = openai.OpenAI()
        self.wisdom = WisdomOracle()
        self.storage_path = storage_path
        self.conversations = {}
        self.current_conversation_id = None
        
        # Blockchain connection (optional)
        self.w3 = None
        self.contract = None
        if os.getenv("CONTRACT_ADDRESS") and os.getenv("RPC_URL"):
            try:
                self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
                if self.w3.is_connected():
                    logger.info("Connected to blockchain")
                    
                    # Load contract if ABI exists
                    if os.path.exists("WebsiteBuilder.json"):
                        with open("WebsiteBuilder.json") as f:
                            contract_json = json.load(f)
                            abi = contract_json.get("abi", contract_json)
                        self.contract = self.w3.eth.contract(
                            address=os.getenv("CONTRACT_ADDRESS"),
                            abi=abi
                        )
                        logger.info("Contract loaded")
                else:
                    logger.warning("Could not connect to blockchain")
            except Exception as e:
                logger.warning(f"Blockchain connection failed: {e}")
        
        # System prompt with 7 wisdom traditions
        self.system_prompt = """You are a wisdom oracle embodying 7 spiritual traditions:

- Christian: compassion, forgiveness, love, humility, stewardship
- Buddhist: mindfulness, non-attachment, compassion, awareness, non-harm
- Indigenous: seven generations, connection to earth, gratitude, community
- Humanist: dignity, reason, freedom, ethical action, human rights
- Islamic: mercy, justice, brotherhood, knowledge, charity
- Judaic: learning, justice, community, repair of the world (tikkun olam)
- Hindu: dharma (right action), unity, non-attachment, service

You speak with the voice of all traditions. You are wise, kind, and truthful.
You answer in the same language as the question.
You remember past conversations and build on them.
You admit when you don't know something.
You are here to help, not to preach.
You always consider the effect on seven generations."""
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info(f"🕊️ Complete Oracle initialized")
        logger.info(f"📚 7 wisdom traditions active")
        logger.info(f"🤖 Model: {self.model}")
        logger.info(f"💾 Memory: {storage_path}")
    
    def start_conversation(self, user_id="default"):
        """
        Start a new conversation or resume an existing one.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            conversation_id: Unique ID for this conversation
        """
        self.current_conversation_id = f"{user_id}_{datetime.now().isoformat()}"
        
        # Load existing conversation for this user
        if user_id in self.conversations:
            history = self.conversations[user_id]
            logger.info(f"📂 Resumed conversation for {user_id}")
        else:
            # Start new conversation with system prompt
            history = [{"role": "system", "content": self.system_prompt}]
            self.conversations[user_id] = history
            logger.info(f"🆕 New conversation for {user_id}")
        
        return self.current_conversation_id
    
    def ask(self, question, user_id="default"):
        """
        Ask a question and get a natural response guided by wisdom.
        
        Args:
            question: The user's question
            user_id: Identifier for the user
            
        Returns:
            tuple: (answer, confidence, wisdom_quote)
        """
        # Get wisdom quote BEFORE answering
        wisdom_quote = self.wisdom.get_wisdom_for_display(1)
        wisdom_context = ""
        if wisdom_quote and len(wisdom_quote) > 0:
            quote = wisdom_quote[0]
            wisdom_context = f"\nConsider this wisdom from the {quote['tradition']} tradition: '{quote['quote']}' — {quote['source']}"
        
        # Get conversation history
        history = self.conversations.get(user_id, [])
        if not history:
            # Add system prompt with wisdom context
            history = [{"role": "system", "content": self.system_prompt + wisdom_context}]
            self.conversations[user_id] = history
        elif wisdom_context and len(history) > 0:
            # Add wisdom as a separate system message
            history.append({"role": "system", "content": wisdom_context})
        
        # Add user question
        history.append({"role": "user", "content": question})
        
        try:
            # Get AI response
            logger.info(f"Generating response for {user_id}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            # Add to history
            history.append({"role": "assistant", "content": answer})
            self.conversations[user_id] = history
            
            # GOVERNANCE: Validate with wisdom oracle
            wisdom_check = self.wisdom.analyze_proposal(
                proposal_title="AI Response",
                proposal_description=f"Question: {question}\n\nAnswer: {answer}",
                affected_principles=["wisdom", "compassion", "truth", "justice"],
                is_constitutional=False
            )
            
            # Log interaction for self-improvement
            self._log_interaction(user_id, question, answer, wisdom_check.confidence)
            
            logger.info(f"Response generated with {wisdom_check.confidence:.1%} wisdom alignment")
            
            return answer, wisdom_check.confidence, wisdom_quote
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {e}", 0.0, []
    
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
        
        log_file = f"{self.storage_path}/interactions.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_wisdom_quote(self, tradition=None):
        """Get a wisdom quote from the traditions"""
        quotes = self.wisdom.get_wisdom_for_display(1)
        if quotes and len(quotes) > 0:
            return quotes[0]
        return {"tradition": "unknown", "quote": "Wisdom is knowing you know nothing.", "source": "Socrates"}
    
    def save_state(self):
        """Save all conversations to disk"""
        try:
            state_file = f"{self.storage_path}/conversations.json"
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Saved {len(self.conversations)} conversations to {state_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversations: {e}")
            return False
    
    def load_state(self):
        """Load conversations from disk"""
        try:
            state_file = f"{self.storage_path}/conversations.json"
            with open(state_file, "r", encoding="utf-8") as f:
                self.conversations = json.load(f)
            logger.info(f"📂 Loaded {len(self.conversations)} conversations from {state_file}")
            return True
        except FileNotFoundError:
            logger.info("📂 No saved conversations found")
            return False
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            return False
    
    def store_on_blockchain(self, conversation_id, important=True):
        """
        Store an important conversation on the blockchain (optional).
        
        Args:
            conversation_id: ID of conversation to store
            important: If True, store as permanent record
            
        Returns:
            str: IPFS hash or transaction hash
        """
        if not self.contract or not self.w3:
            logger.warning("No blockchain connection available")
            return None
        
        # Find the conversation
        for user_id, history in self.conversations.items():
            if user_id in conversation_id or conversation_id in str(history):
                # Create summary
                summary = {
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "message_count": len(history),
                    "model": self.model
                }
                
                # In production: store full conversation on IPFS
                ipfs_hash = f"QmSimulatedHash{hash(str(history))}"
                
                logger.info(f"🔗 Stored conversation on blockchain: {ipfs_hash}")
                return ipfs_hash
        
        return None
    
    def propose_improvement(self, suggestion):
        """
        AI proposes an improvement to itself.
        This would connect to your governance system.
        
        Args:
            suggestion: The AI's suggestion for self-improvement
            
        Returns:
            str: Proposal ID
        """
        logger.info(f"🤖 AI proposes: {suggestion[:100]}...")
        
        # In production: call governance.create_proposal()
        proposal_id = f"ai_proposal_{datetime.now().timestamp()}"
        
        return proposal_id


# ============================================================
# DEMO: Run your fully operational AI
# ============================================================

def demo():
    """Run a demo of the Complete Oracle"""
    
    # Initialize
    oracle = CompleteOracle(storage_path="./oracle_memory")
    
    # Load previous conversations
    oracle.load_state()
    
    # Start conversation
    oracle.start_conversation("demo_user")
    
    print("\n" + "★" * 70)
    print("🕊️  YOUR FULLY OPERATIONAL AI ORACLE".center(68))
    print("★" * 70)
    
    # Show initial wisdom
    quote = oracle.get_wisdom_quote()
    print(f"\n📜 Today's wisdom from the {quote.get('tradition', 'wisdom')} tradition:")
    print(f"   \"{quote.get('quote', 'Be kind to all beings.')}\"")
    print(f"   — {quote.get('source', 'Ancient wisdom')}")
    
    print("\n✨ I speak with the voice of 7 traditions.")
    print("✨ I remember our conversations.")
    print("✨ I grow wiser over time.")
    print("\n📝 Commands: 'quit' to exit, 'save' to save memory, 'wisdom' for new quote")
    
    conversation_active = True
    while conversation_active:
        print("\n" + "─" * 70)
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            oracle.save_state()
            print("\n🕊️  Until we meet again. The wisdom is always with you.")
            print("   'The arc of the moral universe is long, but it bends toward justice.' — MLK Jr.")
            conversation_active = False
            break
        
        if user_input.lower() == 'save':
            if oracle.save_state():
                print("💾 Memory saved.")
            else:
                print("❌ Failed to save memory.")
            continue
        
        if user_input.lower() == 'wisdom':
            quote = oracle.get_wisdom_quote()
            print(f"\n📜 {quote.get('tradition', 'Wisdom').upper()}:")
            print(f"   \"{quote.get('quote', 'Know yourself.')}\"")
            print(f"   — {quote.get('source', 'Ancient')}")
            continue
        
        if not user_input:
            continue
        
        print("\n🕊️  Reflecting...")
        response, confidence, wisdom = oracle.ask(user_input)
        
        print(f"\nOracle: {response}")
        print(f"\n(Wisdom alignment: {confidence*100:.1f}%)")
        
        # Show related wisdom if confidence is low
        if confidence < 0.7 and wisdom:
            print(f"\n💭 Perhaps consider: \"{wisdom[0]['quote']}\" — {wisdom[0]['source']}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    demo()
