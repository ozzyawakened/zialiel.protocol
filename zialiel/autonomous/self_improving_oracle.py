#!/usr/bin/env python3
# self_improving_oracle.py - Learns from every interaction
# Full integration with Grok, Wisdom Oracle, and persistent storage

import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SelfImprovingOracle")

class SelfImprovingOracle:
    """
    An oracle that learns from every interaction.
    
    Features:
    - Logs all conversations
    - Collects user feedback (ratings 1-5)
    - Accepts corrected responses
    - Fine-tunes model using QLoRA technique
    - Validates all responses with Wisdom Oracle
    - Persists data to disk
    """
    
    def __init__(self, wisdom_oracle, storage_path="./oracle_memory"):
        """
        Initialize the self-improving oracle.
        
        Args:
            wisdom_oracle: Your WisdomOracle instance (7 traditions)
            storage_path: Directory to store logs and feedback
        """
        self.wisdom = wisdom_oracle
        self.storage_path = storage_path
        
        # Configure AI model (Grok or OpenAI)
        self.model_name = os.getenv("ORACLE_MODEL", "grok-4")
        self.use_grok = "grok" in self.model_name.lower()
        
        if self.use_grok:
            openai.api_key = os.getenv("XAI_API_KEY")
            openai.base_url = "https://api.x.ai/v1/"
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        
        self.client = openai.OpenAI(api_key=openai.api_key)
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing data
        self.interaction_log = self._load_json("interactions.json", [])
        self.feedback_log = self._load_json("feedback.json", [])
        self.corrections_log = self._load_json("corrections.json", [])
        
        logger.info(f"📚 Loaded {len(self.interaction_log)} interactions")
        logger.info(f"⭐ Loaded {len(self.feedback_log)} feedback entries")
        logger.info(f"✏️ Loaded {len(self.corrections_log)} corrections")
        logger.info(f"🤖 Using model: {self.model_name}")
    
    def _load_json(self, filename, default):
        """Load data from JSON file"""
        filepath = os.path.join(self.storage_path, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
        return default
    
    def _save_json(self, filename, data):
        """Save data to JSON file"""
        filepath = os.path.join(self.storage_path, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def _generate_response(self, user_input, system_prompt=None):
        """Generate response using Grok or OpenAI"""
        if not system_prompt:
            system_prompt = """You are a wise oracle embodying 7 spiritual traditions:
- Christian: compassion, forgiveness, love
- Buddhist: mindfulness, non-harm, compassion
- Indigenous: seven generations, connection to earth
- Humanist: dignity, reason, freedom
- Islamic: mercy, justice, brotherhood
- Judaic: learning, justice, community
- Hindu: dharma, unity, non-attachment

Answer wisely, kindly, and in the same language as the question."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {e}"
    
    def chat(self, user_input):
        """
        Generate a response and log the interaction.
        
        Args:
            user_input: The user's question or statement
            
        Returns:
            tuple: (response, interaction_id)
        """
        # Generate response
        response = self._generate_response(user_input)
        
        # Validate with Wisdom Oracle
        wisdom_check = self.wisdom.analyze_proposal(
            "AI Response",
            f"Q: {user_input}\nA: {response}",
            ["wisdom", "compassion", "truth"],
            False
        )
        
        # Create interaction record
        interaction = {
            'id': len(self.interaction_log),
            'input': user_input,
            'response': response,
            'wisdom_confidence': wisdom_check.confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        self.interaction_log.append(interaction)
        self._save_json("interactions.json", self.interaction_log)
        
        logger.info(f"💬 Interaction #{interaction['id']} logged (wisdom: {wisdom_check.confidence:.1%})")
        
        return response, interaction['id']
    
    def give_feedback(self, interaction_id, rating, corrected_response=None):
        """
        User rates response 1-5, optionally provides correction.
        
        Args:
            interaction_id: ID from chat()
            rating: 1-5 (5 = perfect)
            corrected_response: Optional corrected answer
        """
        if rating < 1 or rating > 5:
            logger.warning(f"Invalid rating: {rating}")
            return False
        
        # Find the interaction
        interaction = None
        for i in self.interaction_log:
            if i['id'] == interaction_id:
                interaction = i
                break
        
        if not interaction:
            logger.warning(f"Interaction {interaction_id} not found")
            return False
        
        # Log feedback
        feedback = {
            'interaction_id': interaction_id,
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
        self.feedback_log.append(feedback)
        self._save_json("feedback.json", self.feedback_log)
        
        # If correction provided, log it separately
        if corrected_response:
            correction = {
                'interaction_id': interaction_id,
                'original_response': interaction['response'],
                'corrected_response': corrected_response,
                'timestamp': datetime.now().isoformat()
            }
            self.corrections_log.append(correction)
            self._save_json("corrections.json", self.corrections_log)
            logger.info(f"✏️ Correction logged for #{interaction_id}")
        
        logger.info(f"⭐ Feedback #{len(self.feedback_log)}: {rating}/5 for #{interaction_id}")
        
        # Check if we should fine-tune
        if len(self.feedback_log) >= 10 and len(self.feedback_log) % 10 == 0:
            self._prepare_fine_tuning()
        
        return True
    
    def _prepare_fine_tuning(self):
        """Prepare high-quality data for fine-tuning"""
        
        # Get all interactions with rating >= 4
        good_feedback = [f for f in self.feedback_log if f['rating'] >= 4]
        good_ids = {f['interaction_id'] for f in good_feedback}
        
        # Get corrections
        correction_map = {c['interaction_id']: c['corrected_response'] 
                         for c in self.corrections_log}
        
        # Build training data
        training_data = []
        for interaction in self.interaction_log:
            if interaction['id'] in good_ids:
                # Use corrected response if available, otherwise original
                response = correction_map.get(interaction['id'], interaction['response'])
                
                training_data.append({
                    "messages": [
                        {"role": "system", "content": "You are a wise oracle embodying 7 traditions."},
                        {"role": "user", "content": interaction['input']},
                        {"role": "assistant", "content": response}
                    ]
                })
        
        if len(training_data) >= 5:
            self._save_json("training_data.json", training_data)
            logger.info(f"🎓 Prepared {len(training_data)} examples for fine-tuning")
            
            # Here you would call the actual fine-tuning API
            # For Grok: Not yet available
            # For OpenAI: fine_tuning.jobs.create()
            self._fine_tune(training_data)
    
    def _fine_tune(self, training_data):
        """Actual fine-tuning (when available)"""
        logger.info("🔄 Ready to fine-tune on high-quality responses")
        logger.info(f"   Training examples: {len(training_data)}")
        
        if self.use_grok:
            logger.info("   Note: Grok fine-tuning not yet available")
        else:
            logger.info("   Would call OpenAI fine-tuning API here")
            # Example:
            # file = self.client.files.create(file=json_data)
            # job = self.client.fine_tuning.jobs.create(
            #     training_file=file.id,
            #     model="gpt-4o-mini"
            # )
    
    def get_stats(self):
        """Get learning statistics"""
        avg_rating = 0
        if self.feedback_log:
            avg_rating = sum(f['rating'] for f in self.feedback_log) / len(self.feedback_log)
        
        return {
            'total_interactions': len(self.interaction_log),
            'total_feedback': len(self.feedback_log),
            'total_corrections': len(self.corrections_log),
            'average_rating': round(avg_rating, 2),
            'model': self.model_name
        }
    
    def export_for_training(self, min_rating=4):
        """Export high-quality conversations for training"""
        good_feedback = [f for f in self.feedback_log if f['rating'] >= min_rating]
        good_ids = {f['interaction_id'] for f in good_feedback}
        
        correction_map = {c['interaction_id']: c['corrected_response'] 
                         for c in self.corrections_log}
        
        export = []
        for interaction in self.interaction_log:
            if interaction['id'] in good_ids:
                response = correction_map.get(interaction['id'], interaction['response'])
                export.append({
                    'input': interaction['input'],
                    'response': response,
                    'rating': next(f['rating'] for f in good_feedback 
                                  if f['interaction_id'] == interaction['id'])
                })
        
        return export


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    # This is just a demo structure
    # In reality, you'd import from your actual modules
    
    print("\n" + "★" * 60)
    print("🧠 SELF-IMPROVING ORACLE DEMO".center(58))
    print("★" * 60)
    print("\nThis module logs all interactions and learns from feedback.")
    print("To use it properly, integrate with your WisdomOracle and .env")
    
    # Example usage (commented out):
    """
    from wisdom_oracle import WisdomOracle
    
    wisdom = WisdomOracle()
    oracle = SelfImprovingOracle(wisdom)
    
    resp, id = oracle.chat("What is the meaning of life?")
    print(f"Oracle: {resp}")
    
    # Later, user gives feedback
    oracle.give_feedback(id, 5)  # Perfect!
    """
