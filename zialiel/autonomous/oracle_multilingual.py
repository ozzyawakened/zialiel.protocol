python
# oracle_multilingual.py
"""
A multilingual interface for the Wisdom Oracle.
Speak in any language, receive wisdom in the same language.
"""

from wisdom_oracle import WisdomOracle
from googletrans import Translator
import time
import random

class MultilingualOracle:
    """
    A Wisdom Oracle that understands and responds in any language.
    Uses Google Translate to bridge between languages and the oracle's wisdom.
    """
    
    def __init__(self):
        # Your original wisdom oracle (7 traditions)
        self.wisdom = WisdomOracle()
        
        # Google Translate client
        self.translator = Translator()
        
        # Supported languages (over 100 supported by Google Translate)
        self.supported_languages = {
            'no': 'Norwegian',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'zh-cn': 'Chinese (Simplified)',
            'ja': 'Japanese',
            'ko': 'Korean',
            'tr': 'Turkish',
            'fa': 'Persian',
            'ur': 'Urdu',
            'he': 'Hebrew',
            'nl': 'Dutch',
            'pl': 'Polish',
            'sv': 'Swedish',
            'da': 'Danish',
            'fi': 'Finnish',
            'el': 'Greek',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'uk': 'Ukrainian',
            'bg': 'Bulgarian',
            'sr': 'Serbian',
            'hr': 'Croatian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'lt': 'Lithuanian',
            'lv': 'Latvian',
            'et': 'Estonian'
        }
        
        # Conversation history
        self.conversation_history = []
        
        print("\n" + "★" * 60)
        print("🌍 THE MULTILINGUAL WISDOM ORACLE".center(58))
        print("★" * 60)
        print(f"\n✅ Oracle initialized with 7 wisdom traditions")
        print(f"🌐 Supports {len(self.supported_languages)}+ languages")
        print(f"🇳🇴 You can speak Norwegian, English, Arabic, Chinese...")
    
    def detect_language(self, text):
        """
        Detect the language of the input text
        
        Args:
            text: The text to detect language for
            
        Returns:
            Language code (e.g., 'no', 'en', 'ar')
        """
        try:
            detection = self.translator.detect(text)
            lang = detection.lang
            return lang
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'en'  # Default to English
    
    def get_language_name(self, lang_code):
        """Get the full language name from a language code"""
        return self.supported_languages.get(lang_code, lang_code)
    
    def ask(self, question, target_lang=None):
        """
        Ask the oracle a question in any language.
        Returns answer in the same language as the question.
        
        Args:
            question: Your question in any language
            target_lang: Optional specific language code (auto-detected if not provided)
            
        Returns:
            The oracle's answer in your language
        """
        
        # Detect source language if not specified
        if not target_lang:
            source_lang = self.detect_language(question)
        else:
            source_lang = target_lang
        
        source_lang_name = self.get_language_name(source_lang)
        print(f"🌐 Detected language: {source_lang_name} ({source_lang})")
        
        # Translate question to English for the oracle
        if source_lang != 'en':
            print("🔄 Translating your question to English...")
            translated = self.translator.translate(question, src=source_lang, dest='en')
            oracle_input = translated.text
            print(f"📝 English: \"{oracle_input[:100]}{'...' if len(oracle_input) > 100 else ''}\"")
        else:
            oracle_input = question
        
        # Extract wisdom principles from the question
        principles = self._extract_principles(oracle_input)
        print(f"🔍 Analyzing through principles: {', '.join(principles)}")
        
        # Ask the wisdom oracle
        result = self.wisdom.analyze_proposal(
            proposal_title="User Question",
            proposal_description=oracle_input,
            affected_principles=principles,
            is_constitutional=False
        )
        
        # Generate a natural language response in English
        english_response = self._generate_response(result, oracle_input)
        
        # Translate back to original language
        if source_lang != 'en':
            print(f"🔄 Translating response back to {source_lang_name}...")
            translated_response = self.translator.translate(english_response, dest=source_lang)
            final_response = translated_response.text
        else:
            final_response = english_response
        
        # Add to conversation history
        self.conversation_history.append({
            'question': question,
            'language': source_lang,
            'answer': final_response,
            'confidence': result.confidence,
            'timestamp': time.time()
        })
        
        return final_response, result.confidence
    
    def _extract_principles(self, text):
        """Extract wisdom principles from the question text"""
        text_lower = text.lower()
        principles = []
        
        keyword_map = {
            "justice": ["justice", "fair", "right", "equality", "discrimination", "unfair"],
            "compassion": ["compassion", "kind", "mercy", "forgive", "forgiveness", "help", "care", "gentle"],
            "stewardship": ["stewardship", "environment", "nature", "earth", "future", "generation", "planet", "sustainable"],
            "freedom": ["freedom", "liberty", "choice", "autonomy", "free", "independent"],
            "community": ["community", "together", "share", "collective", "society", "fellowship", "neighbor"],
            "truth": ["truth", "honest", "real", "authentic", "wisdom", "knowledge"],
            "gratitude": ["gratitude", "thank", "grateful", "appreciation", "blessing"],
            "dignity": ["dignity", "respect", "honor", "value", "worth", "sacred"],
            "love": ["love", "beloved", "cherish", "affection", "heart"],
            "peace": ["peace", "calm", "serenity", "harmony", "tranquil"],
            "hope": ["hope", "faith", "trust", "belief", "optimism"],
            "courage": ["courage", "brave", "strength", "fear", "doubt"]
        }
        
        for principle, keywords in keyword_map.items():
            if any(k in text_lower for k in keywords):
                if principle not in principles:
                    principles.append(principle)
        
        # Default if no principles found
        if not principles:
            principles = ["wisdom"]
        
        return principles
    
    def _generate_response(self, result, original_question):
        """Generate a natural, meaningful response based on the oracle's analysis"""
        
        confidence = result.confidence
        consensus = [t.value for t in result.consensus_traditions]
        dissenting = [t.value for t in result.dissenting_traditions]
        
        # Get a random wisdom quote
        quotes = self.wisdom.get_wisdom_for_display(1)
        quote_text = ""
        if quotes:
            q = quotes[0]
            quote_text = f"\n\nAs {q['tradition'].title()} wisdom reminds us:\n\"{q['quote']}\" — {q['source']}"
        
        # Generate response based on confidence level
        if confidence >= 0.8:
            # Strong alignment
            return f"""✨ The wisdom traditions speak with one voice on this matter.

{len(consensus)} of 7 traditions are in strong agreement: {', '.join(consensus[:3])}{' and others' if len(consensus) > 3 else ''}.

The path forward is clear. Trust in this alignment and move forward with confidence.
{quote_text}"""
        
        elif confidence >= 0.6:
            # Moderate alignment
            return f"""🕊️ There is general agreement among the traditions, though with some nuance.

{len(consensus)} traditions support this: {', '.join(consensus[:3])}{' and others' if len(consensus) > 3 else ''}.
{len(dissenting)} tradition{'s' if len(dissenting) != 1 else ''} {'have' if len(dissenting) != 1 else 'has'} reservations: {', '.join(dissenting[:2])}.

This is a good path, but proceed with awareness of the cautions raised.
{quote_text}"""
        
        elif confidence >= 0.4:
            # Mixed signals
            return f"""🌙 The traditions are divided on this question.

Some see wisdom here: {', '.join(consensus[:2]) if consensus else 'Few'}.
Others urge caution: {', '.join(dissenting[:2]) if dissenting else 'Several'}.

This suggests a need for deeper reflection. Consider both perspectives before deciding.
{quote_text}"""
        
        else:
            # Low alignment
            return f"""⚠️ The traditions counsel careful reconsideration.

Only {len(consensus)} of 7 traditions see alignment here. The majority express concern: {', '.join(dissenting[:3])}.

This may not be the right path, or perhaps the question needs to be reframed. Sit with this in stillness.
{quote_text}"""
    
    def get_wisdom_quote(self, lang='en'):
        """Get a random wisdom quote, optionally translated"""
        quotes = self.wisdom.get_wisdom_for_display(1)
        if not quotes:
            return "Stillhet er også visdom." if lang == 'no' else "Silence is also wisdom."
        
        q = quotes[0]
        quote_text = f"\"{q['quote']}\" — {q['source']}"
        
        # Translate if needed
        if lang != 'en':
            try:
                translated = self.translator.translate(quote_text, dest=lang)
                return f"📜 {q['tradition'].upper()}: {translated.text}"
            except:
                return f"📜 {q['tradition'].upper()}: {quote_text}"
        else:
            return f"📜 {q['tradition'].upper()}: {quote_text}"
    
    def chat(self):
        """Start a multilingual conversation with the oracle"""
        
        print("\n" + "─" * 60)
        print("Ask me anything – in any language. I will answer in the same language.")
        print("Examples: 'Hva er meningen med livet?' (Norwegian), 'ما معنى الحياة؟' (Arabic)")
        print("(Type 'quit', 'exit', or 'avslutt' to end)")
        
        while True:
            print("\n" + "─" * 60)
            question = input("❓ You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye', 'avslutt']:
                print("\n🕊️  Go in peace. The wisdom is always with you.")
                print("🕊️  Gå i fred. Visdommen er alltid med deg.")
                break
            
            if not question:
                continue
            
            print("\n🔮 Consulting the traditions...")
            time.sleep(1)
            
            # Show a wisdom quote while thinking
            detected_lang = self.detect_language(question)
            print(self.get_wisdom_quote(detected_lang))
            print("🤔 Reflecting...")
            time.sleep(1)
            
            # Get answer
            answer, confidence = self.ask(question)
            
            print(f"\n🕊️ Oracle: {answer}")
            print(f"\n(⚖️ Wisdom confidence: {confidence*100:.1f}%)")

