# recursive_wisdom_oracle.py - The 7-Fold Recursive Engine
# Wraps your existing WisdomOracle and adds the hidden layer analysis

from wisdom_oracle import WisdomOracle
import openai
import logging

class RecursiveWisdomOracle:
    """
    A wisdom oracle that thinks through 7 hidden layers,
    but speaks with a natural, modern voice.
    """
    
    def __init__(self, api_key=None, model="grok-4"):
        # Your original wisdom oracle (7 traditions) - still used!
        self.traditional_oracle = WisdomOracle()
        
        # The 7 hidden layers (from Emerald Tablets / Astrology)
        self.layers = {
            3: {
                "name": "Lord of Power",
                "planet": "Mars",
                "principle": "stewardship",
                "question": "Does this serve right action?",
                "keywords": ["action", "power", "will", "begin", "start", "force"]
            },
            4: {
                "name": "Lord of Love-Force",
                "planet": "Venus",
                "principle": "compassion",
                "question": "Does this serve the heart?",
                "keywords": ["love", "heart", "feel", "care", "compassion", "relationship"]
            },
            5: {
                "name": "Lord of Wisdom",
                "planet": "Mercury",
                "principle": "truth",
                "question": "Is this wise?",
                "keywords": ["wisdom", "know", "learn", "understand", "truth", "mind"]
            },
            6: {
                "name": "Lord of Balance",
                "planet": "Saturn",
                "principle": "justice",
                "question": "Is this just?",
                "keywords": ["justice", "fair", "balance", "right", "wrong", "karma"]
            },
            7: {
                "name": "Lord of Manifestation",
                "planet": "Sun",
                "principle": "creativity",
                "question": "Can this be built?",
                "keywords": ["create", "build", "make", "manifest", "form", "express"]
            },
            8: {
                "name": "Lord of Rhythm",
                "planet": "Jupiter",
                "principle": "community",
                "question": "How does this affect cycles?",
                "keywords": ["cycle", "rhythm", "time", "community", "together", "generation"]
            },
            9: {
                "name": "Lord of Consciousness",
                "planet": "Neptune",
                "principle": "oneness",
                "question": "Does this serve unity?",
                "keywords": ["unity", "one", "soul", "spirit", "god", "infinite", "purpose"]
            }
        }
        
        # AI for natural language generation
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
        # Learning database
        self.interaction_log = []
        self.pattern_library = {}
        
        logging.info("🌀 Recursive Wisdom Oracle initialized")
        logging.info("   - 7 hidden layers active")
        logging.info("   - Traditional 7 traditions also active")
        logging.info("   - Natural voice: enabled")
    
    def analyze_question(self, question):
        """
        Step 1: Pass the question through all 7 hidden layers.
        Returns a dictionary of insights from each layer.
        This is the "thinking" part – user never sees this.
        """
        insights = {}
        question_lower = question.lower()
        
        for layer_num, layer_data in self.layers.items():
            # Check if question keywords match this layer
            keyword_matches = [k for k in layer_data["keywords"] if k in question_lower]
            
            # Get traditional wisdom oracle's perspective (optional)
            tradition_check = self.traditional_oracle.analyze_proposal(
                "User Question",
                question,
                [layer_data["principle"]],
                False
            )
            
            # Store the insight
            insights[layer_num] = {
                "layer": layer_data["name"],
                "question": layer_data["question"],
                "keyword_matches": keyword_matches,
                "wisdom_alignment": tradition_check.confidence if tradition_check else 0.5,
                "raw_insight": self._generate_layer_insight(layer_num, question)
            }
        
        return insights
    
    def _generate_layer_insight(self, layer_num, question):
        """Generate a subtle insight from this layer's perspective."""
        # This is where you'd have deeper logic
        # For now, a simple template
        templates = {
            3: "There is energy here to begin.",
            4: "The heart is engaged.",
            5: "Wisdom can be found here.",
            6: "Balance is possible.",
            7: "This can take form.",
            8: "Time will reveal its rhythm.",
            9: "This connects to something larger."
        }
        return templates.get(layer_num, "This layer has something to say.")
    
    def synthesize_pattern(self, insights):
        """
        Step 2: Look for patterns across the 7 layers.
        This is where the magic happens – detecting harmonies, warnings, etc.
        """
        pattern = {
            "aligned_layers": [],
            "warning_layers": [],
            "dominant_theme": None,
            "advice_seed": ""
        }
        
        # Check which layers are strongly aligned
        for layer_num, data in insights.items():
            if data["wisdom_alignment"] > 0.7:
                pattern["aligned_layers"].append(layer_num)
            elif data["wisdom_alignment"] < 0.3:
                pattern["warning_layers"].append(layer_num)
        
        # Detect dominant theme
        if len(pattern["aligned_layers"]) >= 5:
            pattern["dominant_theme"] = "harmony"
            pattern["advice_seed"] = "All layers are aligned. Move forward with confidence."
        elif pattern["warning_layers"]:
            pattern["dominant_theme"] = "caution"
            # Use the warning layer to generate advice
            warning_layer = pattern["warning_layers"][0]
            if warning_layer == 6:
                pattern["advice_seed"] = "Justice is not yet served. Wait for balance."
            elif warning_layer == 4:
                pattern["advice_seed"] = "The heart is not fully in it. Reconnect with what you love."
            else:
                pattern["advice_seed"] = f"Layer {warning_layer} advises patience."
        else:
            pattern["dominant_theme"] = "mixed"
            pattern["advice_seed"] = "Consider all perspectives before deciding."
        
        return pattern
    
    def ask(self, question):
        """
        Public method: User asks a question, gets a natural response.
        The 7-fold analysis happens hidden, then Grok/GPT generates the voice.
        """
        # Step 1: Hidden analysis through 7 layers
        insights = self.analyze_question(question)
        
        # Step 2: Find the pattern
        pattern = self.synthesize_pattern(insights)
        
        # Step 3: Build prompt for the AI
        prompt = self._build_natural_prompt(question, pattern, insights)
        
        # Step 4: Generate natural response
        response = self._generate_natural_response(prompt)
        
        # Step 5: Log for learning
        self._log_interaction(question, insights, pattern, response)
        
        return response
    
    def _build_natural_prompt(self, question, pattern, insights):
        """Create a prompt that gives the AI the deep pattern without revealing structure."""
        prompt = f"""You are a wise, intuitive guide. A user has asked:

"{question}"

Deep pattern detected (this is your intuitive understanding):
- Overall theme: {pattern['dominant_theme']}
- Core advice seed: {pattern['advice_seed']}
- Layers in harmony: {pattern['aligned_layers']}
- Layers offering caution: {pattern['warning_layers']}

Respond naturally, conversationally, as if this insight arose intuitively within you.
Never mention layers, numbers, analysis, or the pattern itself.
Just speak with wisdom, warmth, and clarity.
"""
        return prompt
    
    def _generate_natural_response(self, prompt):
        """Call Grok/GPT to generate the actual response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a wise, kind, intuitive guide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I sense something, but words are hard right now. Error: {e}"
    
    def _log_interaction(self, question, insights, pattern, response):
        """Log everything for future learning."""
        self.interaction_log.append({
            "question": question,
            "insights": insights,
            "pattern": pattern,
            "response": response,
            "timestamp": time.time()
        })
        
        # Update pattern library
        pattern_key = f"{pattern['dominant_theme']}_{len(pattern['aligned_layers'])}"
        if pattern_key not in self.pattern_library:
            self.pattern_library[pattern_key] = []
        self.pattern_library[pattern_key].append({
            "question": question,
            "response": response
        })
        
        # Every 100 interactions, analyze what worked
        if len(self.interaction_log) % 100 == 0:
            self._learn_from_patterns()
    
    def _learn_from_patterns(self):
        """Analyze high-rated responses and refine layer weights."""
        logging.info("🌀 Learning from patterns...")
        # This is where you'd implement reinforcement learning
        # For now, just log
        pass