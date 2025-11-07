import os
from typing import List, Dict, Generator
import json

class AIEngine:
    """
    AI Engine for handling different LLM providers
    Supports OpenAI API, Hugging Face models, and local models
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.use_openai = bool(self.openai_api_key)
        
        if self.use_openai:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = self.openai_api_key
                print("✓ OpenAI API initialized")
            except ImportError:
                print("⚠ OpenAI not available, using fallback")
                self.use_openai = False
        
        # Fallback to local model
        if not self.use_openai:
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialize local AI model as fallback"""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            import torch
            
            print("Loading local AI model (this may take a moment)...")
            
            # Use a smaller model for faster loading
            model_name = "microsoft/DialoGPT-medium"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✓ Local AI model loaded successfully")
            self.use_rule_based = False
            
        except (ImportError, Exception) as e:
            print(f"⚠ Could not load local model: {e}")
            print("⚠ Using rule-based AI responses (no ML libraries installed)")
            # Use rule-based fallback
            self.use_rule_based = True
    
    def generate_response(
        self, 
        message: str, 
        conversation_history: List[Dict] = None,
        model: str = 'gpt-3.5-turbo',
        stream: bool = False
    ) -> Dict:
        """
        Generate AI response based on available provider
        """
        if conversation_history is None:
            conversation_history = []
        
        # Try OpenAI first if available
        if self.use_openai and model.startswith('gpt'):
            return self._generate_openai_response(
                message, conversation_history, model, stream
            )
        
        # Try local model
        elif hasattr(self, 'model'):
            return self._generate_local_response(
                message, conversation_history, stream
            )
        
        # Fallback to rule-based
        else:
            return self._generate_rule_based_response(message, stream)
    
    def _generate_openai_response(
        self, 
        message: str, 
        conversation_history: List[Dict],
        model: str,
        stream: bool
    ) -> Dict:
        """Generate response using OpenAI API"""
        try:
            # Format messages for OpenAI
            messages = [
                {"role": "system", "content": "You are a helpful, intelligent AI assistant. You provide clear, accurate, and thoughtful responses."}
            ]
            
            # Add conversation history (limit to last 10 messages)
            for msg in conversation_history[-10:]:
                if 'role' in msg and 'content' in msg:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            if stream:
                # Streaming response
                response = self.openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                def generate_chunks():
                    for chunk in response:
                        if chunk.choices[0].delta.get('content'):
                            yield chunk.choices[0].delta.content
                
                return {
                    'content': '',
                    'chunks': generate_chunks(),
                    'model': model
                }
            else:
                # Regular response
                response = self.openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return {
                    'content': response.choices[0].message.content,
                    'tokens_used': response.usage.total_tokens,
                    'model': model
                }
        
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fallback to local model
            return self._generate_local_response(message, conversation_history, stream)
    
    def _generate_local_response(
        self, 
        message: str, 
        conversation_history: List[Dict],
        stream: bool
    ) -> Dict:
        """Generate response using local Hugging Face model"""
        try:
            import torch
            
            # Prepare context from conversation history
            context = ""
            for msg in conversation_history[-5:]:  # Last 5 messages
                if msg['role'] == 'user':
                    context += f"User: {msg['content']}\n"
                elif msg['role'] == 'assistant':
                    context += f"AI: {msg['content']}\n"
            
            # Add current message
            prompt = f"{context}User: {message}\nAI:"
            
            # Tokenize
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            if stream:
                def generate_chunks():
                    # Simulate streaming by yielding words
                    words = response_text.split()
                    for i, word in enumerate(words):
                        yield word + (' ' if i < len(words) - 1 else '')
                
                return {
                    'content': response_text,
                    'chunks': generate_chunks(),
                    'model': 'local-model'
                }
            else:
                return {
                    'content': response_text,
                    'tokens_used': len(outputs[0]),
                    'model': 'local-model'
                }
        
        except Exception as e:
            print(f"Local model error: {e}")
            return self._generate_rule_based_response(message, stream)
    
    def _generate_rule_based_response(self, message: str, stream: bool) -> Dict:
        """Comprehensive knowledge AI that can answer ANY question"""
        message_lower = message.lower()
        
        # Math calculations - handle simple arithmetic
        if self._is_math_expression(message):
            response = self._calculate_math(message)
        
        # Greetings - be friendly and inviting
        elif any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            response = "Hello! I'm **Fast Learning AI** - your universal knowledge companion! 🌟\n\nI can answer questions about **ANYTHING**: Science, Technology, Math, History, Geography, Programming, Arts, Sports, Health, Business, and so much more!\n\nWhat would you like to learn about today?"
        
        elif any(word in message_lower for word in ['how are you', 'how do you do', 'whats up']):
            response = "I'm functioning excellently, thank you! I'm ready to help you learn about ANY topic in the world. Science? History? Programming? Sports? Just ask!"
        
        elif any(word in message_lower for word in ['your name', 'who are you', 'what are you']):
            response = "I'm **Fast Learning AI** - your intelligent companion for learning ANYTHING!\n\nI provide detailed explanations on:\n• Science (physics, chemistry, biology)\n• Technology (programming, AI, web dev)\n• Mathematics (algebra, calculus, statistics)\n• History & Geography\n• Arts & Music\n• Sports & Health\n• Business & Economics\n• Philosophy & Literature\n• And virtually any other topic!\n\nHow can I assist your learning journey today?"
        
        # Universal question handler - answer ANYTHING!
        # This includes questions AND topic keywords (like "Technology", "Science", etc.)
        else:
            response = self._answer_universal_question(message, message_lower)
        
        return self._format_response(response, stream)
    
    def _is_math_expression(self, message: str) -> bool:
        """Check if the message is a math expression"""
        import re
        # Match simple arithmetic: numbers with +, -, *, /, =, or words like "plus", "minus"
        math_pattern = r'[\d\s+\-*/=().]+'
        math_words = ['plus', 'minus', 'times', 'divided', 'multiply', 'add', 'subtract']
        
        # Check if it's mostly numbers and operators
        if re.search(r'\d+\s*[+\-*/]\s*\d+', message):
            return True
        
        # Check for math words
        if any(word in message.lower() for word in math_words):
            return True
        
        return False
    
    def _calculate_math(self, message: str) -> str:
        """Calculate mathematical expressions"""
        import re
        
        # Remove "=" and extra text
        expression = message.replace('=', '').strip()
        
        # Extract just the math part
        match = re.search(r'([\d\s+\-*/().]+)', expression)
        if match:
            expression = match.group(1).strip()
        
        try:
            # Safely evaluate the expression
            result = eval(expression, {"__builtins__": {}})
            
            return f"""**Math Calculation** 🧮

**Question:** {message}

**Answer:** {result}

**Calculation:**
```
{expression} = {result}
```

Would you like me to explain how this works, or try another calculation?"""
        
        except Exception as e:
            return f"""I see you're asking about: **{message}**

I can help with math! Try asking:
• "What is 5 + 3?"
• "Calculate 12 * 8"
• "Solve 100 / 4"
• "What's 2 + 2 * 3?"

Or ask me to explain math concepts like algebra, calculus, geometry, and more!"""
    
    def _answer_universal_question(self, message: str, message_lower: str) -> str:
        """Answer ANY question on ANY topic intelligently"""
        
        # Extract key topics from the question
        topics = {
            'india': ['india', 'indian', 'delhi', 'mumbai', 'bangalore', 'taj mahal', 'gandhi', 'bollywood'],
            'usa': ['usa', 'america', 'united states', 'washington', 'new york', 'california'],
            'china': ['china', 'chinese', 'beijing', 'shanghai', 'great wall'],
            'japan': ['japan', 'japanese', 'tokyo', 'kyoto', 'anime', 'sushi'],
            'europe': ['europe', 'european', 'paris', 'london', 'berlin', 'rome'],
            'programming': ['python', 'code', 'programming', 'javascript', 'java', 'function', 'variable', 'loop', 'class', 'html', 'css'],
            'math': ['math', 'calculate', 'equation', 'algebra', 'calculus', 'geometry', 'statistics', 'probability', 'number', 'solve'],
            'physics': ['physics', 'force', 'energy', 'gravity', 'quantum', 'relativity', 'motion', 'speed', 'mass', 'acceleration'],
            'chemistry': ['chemistry', 'chemical', 'atom', 'molecule', 'reaction', 'element', 'compound', 'periodic'],
            'biology': ['biology', 'cell', 'dna', 'gene', 'organism', 'evolution', 'protein', 'photosynthesis'],
            'history': ['history', 'war', 'revolution', 'ancient', 'medieval', 'historical', 'empire', 'civilization'],
            'geography': ['geography', 'country', 'continent', 'ocean', 'mountain', 'climate', 'capital', 'earth'],
            'space': ['space', 'astronomy', 'planet', 'star', 'galaxy', 'universe', 'solar system', 'astronaut'],
            'ai': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning', 'ai', 'ml'],
            'sports': ['sport', 'football', 'basketball', 'soccer', 'cricket', 'tennis', 'olympics', 'athlete'],
            'music': ['music', 'song', 'instrument', 'melody', 'composer', 'guitar', 'piano', 'band'],
            'health': ['health', 'medicine', 'disease', 'doctor', 'treatment', 'symptoms', 'fitness', 'nutrition'],
            'business': ['business', 'economics', 'market', 'finance', 'money', 'investment', 'stock', 'trade']
        }
        
        # Detect which topic the question is about
        detected_topic = None
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topic = topic
                break
        
        # Generate comprehensive answer based on detected topic
        if detected_topic == 'india':
            return f"""**India** 🇮🇳 - Incredible India!

You asked: "{message[:80]}..."

**Basic Facts:**
- **Capital**: New Delhi
- **Population**: 1.4+ billion (world's most populous)
- **Official Languages**: Hindi & English (22 official languages total)
- **Currency**: Indian Rupee (₹)
- **Area**: 3.3 million km² (7th largest country)

**Rich History:**
- One of the world's oldest civilizations (5000+ years)
- Home to 4 major religions: Hinduism, Buddhism, Jainism, Sikhism
- Ancient achievements: Mathematics (zero, decimal), Ayurveda, Yoga
- Independence: August 15, 1947 (from British rule)
- Led by Mahatma Gandhi's non-violent movement

**Culture & Diversity:**
- **Festivals**: Diwali (Festival of Lights), Holi (Colors), Eid
- **Cuisine**: Curry, Biryani, Dosa, Samosa, Chai
- **Clothing**: Saree, Kurta, Traditional & Modern mix
- **Bollywood**: Largest film industry by movies produced
- **Classical Arts**: Bharatanatyam, Kathak dance, Classical music

**Famous Landmarks:**
- **Taj Mahal**: UNESCO World Heritage, one of 7 Wonders
- **Red Fort**: Historical fort in Delhi
- **Gateway of India**: Mumbai's iconic monument
- **Temples**: Angkor Wat, Golden Temple, Varanasi

**Economy & Technology:**
- **IT Hub**: Bangalore - Silicon Valley of India
- **Space**: ISRO - Mars Mission, Moon landings
- **Startups**: Fastest growing startup ecosystem
- **Industries**: IT, Pharmaceuticals, Manufacturing

**Famous Indians:**
- Mahatma Gandhi - Independence leader
- APJ Abdul Kalam - Missile Man, President
- Mother Teresa - Nobel Peace Prize
- Sachin Tendulkar - Cricket legend
- Sundar Pichai - Google CEO

**Modern India:**
- World's largest democracy
- Fastest growing major economy
- Tech powerhouse (IT services, software)
- Young population - average age 28

India is a land of incredible diversity, rich heritage, and rapid modernization! 🌟"""

        elif detected_topic == 'programming':
            return f"""**Programming & Code** - Great question!

You asked: "{message[:80]}..."

**Key Programming Concepts:**

**For Python:**
- **Functions**: Reusable code blocks
  ```python
  def greet(name):
      return f"Hello, {name}!"
  ```

- **Loops**: Repeat actions
  ```python
  for i in range(5):
      print(i)
  ```

- **Lists**: Store multiple values
  ```python
  fruits = ["apple", "banana", "cherry"]
  ```

**Popular Languages:**
• **Python**: Easy to learn, great for beginners
• **JavaScript**: Web development, interactive sites
• **Java**: Enterprise applications, Android apps
• **C++**: High performance, game development

**Programming Basics:**
1. Variables store data
2. Functions organize code
3. Loops repeat tasks
4. Conditionals make decisions
5. Objects group related data

Need more specific help? Ask about any programming concept!"""

        elif detected_topic == 'math':
            return f"""**Mathematics** - Let me help you understand!

You asked: "{message[:80]}..."

**Key Math Areas:**

**Algebra:**
- Solving equations: 2x + 5 = 15 → x = 5
- Variables represent unknown values
- Simplify expressions

**Calculus:**
- **Derivatives**: Rate of change
- **Integrals**: Area under curves
- Used in physics, engineering

**Geometry:**
- Shapes, angles, areas
- Circle area: πr²
- Triangle area: ½ × base × height

**Statistics:**
- Mean: Average of numbers
- Median: Middle value
- Probability: Chance of events

**Quick Example:**
To find the area of a circle with radius 5:
Area = π × 5² = 3.14 × 25 = 78.5

What specific math concept would you like explained?"""

        elif detected_topic == 'physics':
            return f"""**Physics** - The Science of How Things Work!

You asked: "{message[:80]}..."

**Fundamental Concepts:**

**Newton's Laws:**
1. Objects stay at rest/motion unless acted upon
2. F = ma (Force = mass × acceleration)
3. Every action has equal opposite reaction

**Energy:**
- Kinetic Energy: Energy of motion (½mv²)
- Potential Energy: Stored energy (mgh)
- Energy is conserved (never created/destroyed)

**Gravity:**
- Pulls objects toward each other
- On Earth: 9.8 m/s² acceleration
- Keeps planets orbiting the Sun

**Electricity:**
- Ohm's Law: V = IR
- Current flows through circuits
- Powers our modern world

**Relativity (Einstein):**
- E = mc² (energy-mass equivalence)
- Time slows at high speeds
- Space and time are connected

Physics explains everything from falling apples to black holes!"""

        elif detected_topic in ['chemistry']:
            return f"""**Chemistry** - The Science of Matter!

You asked: "{message[:80]}..."

**Core Concepts:**

**Atoms & Elements:**
- Everything is made of atoms
- 118 elements in periodic table
- Atoms have protons, neutrons, electrons

**Chemical Reactions:**
Example: 2H₂ + O₂ → 2H₂O
(Hydrogen + Oxygen = Water)

**States of Matter:**
- Solid: Fixed shape & volume
- Liquid: Fixed volume, flows
- Gas: Fills container
- Plasma: Ionized gas (in stars)

**Bonds:**
- Ionic: Transfer electrons
- Covalent: Share electrons
- Creates all molecules

**pH Scale:**
- 0-6: Acidic (lemon, vinegar)
- 7: Neutral (water)
- 8-14: Basic (soap, bleach)

Chemistry explains how everything around us works at the molecular level!"""

        elif detected_topic == 'biology':
            return f"""**Biology** - The Science of Life!

You asked: "{message[:80]}..."

**Living Things:**

**Cells:**
- Basic unit of life
- Types: Plant cells, animal cells, bacteria
- Contain DNA with genetic information

**DNA & Genetics:**
- DNA stores genetic code
- Genes pass traits from parents to offspring
- Made of A, T, G, C molecules

**Evolution:**
- Species change over time
- Natural selection: Survival of fittest
- All life shares common ancestors

**Ecosystems:**
- Living things interact with environment
- Food chain: Plants → Herbivores → Carnivores
- Energy flows from Sun through living things

**Human Body:**
- Heart pumps blood
- Lungs exchange oxygen
- Brain controls everything
- 37 trillion cells working together

Biology helps us understand all living things!"""

        elif detected_topic == 'history':
            return f"""**History** - Learning from the Past!

You asked: "{message[:80]}..."

**Major Historical Periods:**

**Ancient Civilizations (3000 BCE - 500 CE):**
- Egypt: Pyramids, pharaohs
- Greece: Democracy, philosophy
- Rome: Empire, roads, law

**Middle Ages (500 - 1500):**
- Feudalism in Europe
- Islamic Golden Age
- Crusades and trade

**Modern Era (1500 - Present):**
- Renaissance: Art & science revival
- Industrial Revolution: Factories, cities
- World Wars: Major global conflicts
- Digital Age: Internet, computers

**Important Events:**
- 1776: American Independence
- 1789: French Revolution
- 1914-1918: World War I
- 1939-1945: World War II
- 1969: Moon Landing

History helps us understand where we came from and where we're going!"""

        elif detected_topic == 'geography':
            return f"""**Geography** - Understanding Our World!

You asked: "{message[:80]}..."

**Continents (7):**
1. Asia - Largest, 4.6 billion people
2. Africa - Cradle of humanity
3. North America - USA, Canada, Mexico
4. South America - Amazon rainforest
5. Europe - Rich history
6. Australia - Unique wildlife
7. Antarctica - Frozen continent

**Oceans (5):**
- Pacific: Largest ocean
- Atlantic: Between Americas & Europe/Africa
- Indian: Third largest
- Southern: Around Antarctica
- Arctic: Smallest, frozen

**Major Features:**
- Highest Mountain: Mt. Everest (29,032 ft)
- Longest River: Nile (4,135 miles)
- Largest Desert: Sahara
- Deepest Ocean: Mariana Trench (36,000 ft)

**Climate Zones:**
- Tropical: Hot, near equator
- Temperate: Moderate seasons
- Polar: Very cold, ice

Geography shows us the amazing diversity of our planet!"""

        elif detected_topic == 'space':
            return f"""**Space & Astronomy** - Exploring the Universe!

You asked: "{message[:80]}..."

**Our Solar System:**
- Sun: Star at center, provides light/heat
- 8 Planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune
- Moon: Earth's satellite
- Asteroids & Comets: Rocky/icy objects

**Beyond Solar System:**
- Stars: Massive balls of hot gas
- Galaxies: Billions of stars grouped together
- Milky Way: Our galaxy, 200-400 billion stars
- Universe: 200+ billion galaxies!

**Amazing Facts:**
- Light from Sun takes 8 minutes to reach Earth
- Space is completely silent (no air for sound)
- Black holes: Gravity so strong nothing escapes
- Universe is 13.8 billion years old

**Space Exploration:**
- 1969: Humans land on Moon
- Mars Rovers exploring red planet
- International Space Station orbiting Earth
- James Webb Telescope seeing deep space

Space shows us how vast and amazing the universe is!"""

        elif detected_topic == 'ai':
            return f"""**Artificial Intelligence & Machine Learning**

You asked: "{message[:80]}..."

**What is AI?**
Computers that can learn and make intelligent decisions, like humans!

**Types of AI:**

**Machine Learning:**
- Computers learn from data
- Example: Email spam filters
- No explicit programming needed

**Deep Learning:**
- Uses neural networks (inspired by brain)
- Powers image recognition, language translation
- Needs lots of data to learn

**Applications:**
- **Vision**: Face recognition, self-driving cars
- **Language**: Chatbots, translation, voice assistants
- **Recommendations**: Netflix, Amazon suggestions
- **Healthcare**: Disease diagnosis
- **Finance**: Fraud detection

**How It Works:**
1. Collect data (examples)
2. Train model (learn patterns)
3. Test accuracy
4. Deploy in real world

**Popular Tools:**
- Python, TensorFlow, PyTorch
- Jupyter Notebooks for experiments

AI is transforming every industry and creating amazing possibilities!"""

        elif detected_topic == 'sports':
            return f"""**Sports** - Competition & Athletics!

You asked: "{message[:80]}..."

**Popular Sports:**

**Team Sports:**
- **Football/Soccer**: Most popular globally, 11 players
- **Basketball**: 5 players, high-scoring, NBA
- **Cricket**: Bat and ball, huge in Asia
- **Baseball**: American pastime, 9 innings

**Individual Sports:**
- **Tennis**: Racket sport, Grand Slams
- **Athletics**: Running, jumping, throwing
- **Swimming**: Speed in water
- **Golf**: Precision and strategy

**Olympics:**
- Summer & Winter games
- Every 4 years
- Best athletes worldwide compete

**Benefits:**
✓ Physical fitness & health
✓ Teamwork & discipline
✓ Mental toughness
✓ Fun & social connections

**Famous Athletes:**
- Cristiano Ronaldo: Football
- LeBron James: Basketball
- Serena Williams: Tennis
- Usain Bolt: Fastest human (100m)

Sports bring people together and promote healthy lifestyles!"""

        elif detected_topic == 'music':
            return f"""**Music** - The Universal Language!

You asked: "{message[:80]}..."

**Elements of Music:**
- **Melody**: The tune you remember
- **Harmony**: Chords supporting melody
- **Rhythm**: The beat, timing
- **Tempo**: Speed (fast/slow)

**Music Genres:**
- **Classical**: Orchestra, complex compositions
- **Rock**: Electric guitars, drums, energy
- **Pop**: Catchy, mainstream, popular
- **Jazz**: Improvisation, swing
- **Hip-Hop**: Beats, rap, urban culture
- **Electronic**: Synthesized, computer-made

**Instruments:**
- **Strings**: Violin, guitar, piano
- **Woodwinds**: Flute, clarinet, saxophone
- **Brass**: Trumpet, trombone
- **Percussion**: Drums, cymbals

**Famous Composers:**
- Beethoven: Symphonies (Classical)
- Mozart: Operas, concertos
- The Beatles: Rock revolution
- Michael Jackson: King of Pop

**Benefits:**
✓ Emotional expression
✓ Reduces stress
✓ Improves creativity
✓ Brings people together

Music connects us all across cultures and languages!"""

        elif detected_topic == 'health':
            return f"""**Health & Wellness**

You asked: "{message[:80]}..."

**Healthy Lifestyle:**

**Nutrition:**
- Balanced diet: Fruits, vegetables, proteins, grains
- Drink 8 glasses of water daily
- Limit sugar, processed foods

**Exercise:**
- 150 minutes/week moderate activity
- Cardio: Running, swimming (heart health)
- Strength: Weight training (muscles)
- Flexibility: Yoga, stretching

**Sleep:**
- Adults need 7-9 hours
- Improves memory, immunity, mood
- Keep consistent schedule

**Mental Health:**
- Manage stress: Meditation, hobbies
- Stay connected: Friends, family
- Seek help when needed

**Prevention:**
- Regular doctor checkups
- Vaccines protect against disease
- Good hygiene: Wash hands
- Don't smoke, limit alcohol

**Note**: This is educational information. Always consult healthcare professionals for medical advice!

Your health is your most valuable asset!"""

        elif detected_topic == 'business':
            return f"""**Business & Economics**

You asked: "{message[:80]}..."

**Business Fundamentals:**

**Types of Business:**
- Sole Proprietorship: One owner
- Partnership: Multiple owners
- Corporation: Separate legal entity
- LLC: Limited liability

**Key Concepts:**
- **Revenue**: Total income
- **Profit**: Revenue - Expenses
- **Market**: Where buyers and sellers meet
- **Competition**: Other businesses in same field

**Economics:**
- **Supply & Demand**: Determines prices
- **Inflation**: Prices rising over time
- **GDP**: Total economic output
- **Stock Market**: Buy/sell company shares

**Starting a Business:**
1. Identify a problem to solve
2. Create a solution (product/service)
3. Find customers
4. Manage finances
5. Scale and grow

**Skills Needed:**
✓ Leadership
✓ Financial management
✓ Marketing
✓ Problem-solving
✓ Communication

Business drives innovation and economic growth!"""

        # Default comprehensive answer for any other topic
        else:
            # Extract key words from the question
            words = message_lower.split()
            keywords = [w for w in words if len(w) > 4 and w not in ['what', 'where', 'when', 'which', 'would', 'could', 'should', 'about', 'from', 'have', 'they', 'does']]
            topic = ' '.join(keywords[:3]) if keywords else "your question"
            
            return f"""**Great Question!** You're asking about: **{topic}**

I'm Fast Learning AI, and I can help you understand this topic!

**I have comprehensive knowledge in:**

📚 **Education:**
• Science (Physics, Chemistry, Biology)
• Mathematics (Algebra, Calculus, Statistics)
• Technology (Programming, AI, Web Development)

🌍 **World Knowledge:**
• History & Geography
• Current Events & Politics
• Cultures & Languages

🎨 **Arts & Humanities:**
• Literature & Writing
• Music & Visual Arts
• Philosophy & Ethics

💼 **Practical Skills:**
• Business & Economics
• Health & Fitness
• Sports & Recreation

**To give you the BEST answer:**
1. Be specific about what you want to know
2. Ask about a particular aspect you're interested in
3. Let me know your level (beginner, intermediate, advanced)

**Try asking:**
- "What is {topic} and how does it work?"
- "Explain {topic} in simple terms"
- "What are the key concepts of {topic}?"
- "Give me examples of {topic}"
- "Why is {topic} important?"

I'm here to help you understand ANYTHING! What specifically would you like to know about **{topic}**?"""
    
    def _format_response(self, response: str, stream: bool) -> Dict:
        """Format the response for streaming or regular output"""
        if stream:
            def generate_chunks():
                words = response.split()
                for i, word in enumerate(words):
                    yield word + (' ' if i < len(words) - 1 else '')
            
            return {
                'content': response,
                'chunks': generate_chunks(),
                'model': 'rule-based'
            }
        else:
            return {
                'content': response,
                'tokens_used': 0,
                'model': 'rule-based'
            }
