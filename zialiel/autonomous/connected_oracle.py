#!/usr/bin/env python3
# oracle_multilingual.py – Enhanced with Grok and .env support

"""
A multilingual interface for the Wisdom Oracle.
Speak in any language, receive wisdom in the same language.
Now with Grok AI for deeper responses.
"""

from wisdom_oracle import WisdomOracle
from deep_translator import GoogleTranslator
import openai
import os
import time
import random
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultilingualOracle")

class MultilingualOracle:
    """
    A Wisdom Oracle that understands and responds in any language.
    Uses Grok AI for wisdom and Google Translate for languages.
    """
    
    def __init__(self):
        # Your original wisdom oracle (7 traditions)
        self.wisdom = WisdomOracle()
        
        # Configure Grok/xAI
        self.use_grok = "grok" in os.getenv("ORACLE_MODEL", "").lower()
        if self.use_grok:
            openai.api_key = os.getenv("XAI_API_KEY")
            openai.base_url = "https://api.x.ai/v1/"
            self.model = os.getenv("ORACLE_MODEL", "grok-4")
            self.client = openai.OpenAI(api_key=openai.api_key)
            logger.info(f"Using Grok: {self.model}")
        
        # Translation setup
        self.translator = GoogleTranslator()
        
        # Supported languages (over 100 supported)
        self.supported_languages = {
            'no': 'Norwegian', 'en': 'English', 'es': 'Spanish', 
            'fr': 'French', 'de': 'German', 'ar': 'Arabic',
            'zh-cn': 'Chinese', 'hi': 'Hindi', 'ru': 'Russian'
        }
        
        # Conversation history
        self.conversation_history = []
        self.translation_cache = {}  # Cache translations
        
        print("\n" + "★" * 60)
        print("🌍 THE MULTILINGUAL WISDOM ORACLE".center(58))
        print("★" * 60)
        print(f"\n✅ Oracle initialized with 7 wisdom traditions")
        print(f"🤖 AI: {self.model if self.use_grok else 'Rule-based'}")
        print(f"🌐 Supports {len(self.supported_languages)}+ languages")
        print(f"🇳🇴 You can speak Norwegian, English, Arabic, Chinese...")
    
    def detect_language(self, text):
        """Detect language of input text"""
        try:
            # Try using langdetect if available
            from langdetect import detect
            return detect(text)
        except:
            # Fallback to simple detection
            if any(ord(c) > 0x0600 and ord(c) < 0x06FF for c in text):
                return 'ar'
            return 'en'
    
    def translate(self, text, source='auto', target='en', use_cache=True):
        """Translate text with caching"""
        cache_key = f"{source}:{target}:{text[:50]}"
        if use_cache and cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            translator = GoogleTranslator(source=source, target=target)
            result = translator.translate(text)
            self.translation_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def ask(self, question, target_lang=None):
        """Ask the oracle a question in any language"""
        
        # Detect source language
        source_lang = target_lang or self.detect_language(question)
        source_lang_name = self.supported_languages.get(source_lang, source_lang)
        print(f"🌐 Language: {source_lang_name}")
        
        # Translate to English for processing
        if source_lang != 'en':
            oracle_input = self.translate(question, source=source_lang, target='en')
            print(f"📝 English: \"{oracle_input[:100]}...\"")
        else:
            oracle_input = question
        
        # Extract principles
        principles = self._extract_principles(oracle_input)
        
        # Get wisdom analysis
        result = self.wisdom.analyze_proposal(
            "User Question", oracle_input, principles, False
        )
        
        # Generate response (using Grok if available)
        if self.use_grok:
            english_response = self._generate_grok_response(result, oracle_input)
        else:
            english_response = self._generate_rule_response(result, oracle_input)
        
        # Translate back
        if source_lang != 'en':
            final_response = self.translate(
                english_response, source='en', target=source_lang
            )
        else:
            final_response = english_response
        
        # Log conversation
        self.conversation_history.append({
            'question': question, 'language': source_lang,
            'answer': final_response, 'confidence': result.confidence
        })
        
        return final_response, result.confidence
    
    def _generate_grok_response(self, result, question):
        """Generate response using Grok AI"""
        consensus = [t.value for t in result.consensus_traditions]
        confidence = result.confidence
        
        prompt = f"""You are a wisdom oracle embodying 7 traditions.
A question was asked. The wisdom oracle analysis shows:
- Confidence: {confidence:.0%}
- Traditions in agreement: {', '.join(consensus[:5])}

Question: {question}

Respond wisely, naturally, and in a way that honors all traditions."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _generate_rule_response(self, result, question):
        """Original rule-based response generation"""
        # [Your existing _generate_response code here]
        confidence = result.confidence
        if confidence >= 0.8:
            return f"✨ The traditions speak with one voice. Proceed with confidence."
        elif confidence >= 0.5:
            return f"🕊️ There is general agreement, but proceed with awareness."
        else:
            return f"⚠️ The traditions counsel reconsideration."
    
    def _extract_principles(self, text):
        """Extract wisdom principles from text"""
        # [Your existing _extract_principles code here]
        principles = []
        keyword_map = {
            "justice": ["justice", "fair", "rights"],
            "compassion": ["compassion", "kind", "mercy"],
            "stewardship": ["stewardship", "environment", "earth"],
        }
        for principle, keywords in keyword_map.items():
            if any(k in text.lower() for k in keywords):
                principles.append(principle)
        return principles or ["wisdom"]
    
    def chat(self):
        """Start multilingual conversation"""
        print("\nAsk me anything – in any language.")
        while True:
            question = input("\n❓ You: ").strip()
            if question.lower() in ['quit', 'exit', 'avslutt']:
                print("\n🕊️  Gå i fred. Visdommen er alltid med deg.")
                break
            if not question:
                continue
            
            answer, conf = self.ask(question)
            print(f"\n🕊️ Oracle: {answer}")
            print(f"(⚖️ {conf:.0%})")

if __name__ == "__main__":
    oracle = MultilingualOracle()
    oracle.chat()
