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
            
        except Exception as e:
            print(f"⚠ Could not load local model: {e}")
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
        """Simple rule-based fallback response"""
        message_lower = message.lower()
        
        # Simple pattern matching with more helpful responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            response = "Hello! I'm your AI learning assistant. I'm here to help you learn faster and answer your questions. What would you like to learn about today?"
        
        elif any(word in message_lower for word in ['how are you', 'how do you do', 'whats up']):
            response = "I'm functioning well, thank you! I'm ready to help you learn anything you'd like. Whether it's science, programming, mathematics, history, or any other topic - just ask!"
        
        elif any(word in message_lower for word in ['your name', 'who are you', 'what are you']):
            response = "I'm Fast Learning AI - your intelligent learning companion! I'm designed to help you understand complex topics, answer questions, and accelerate your learning journey. How can I assist your learning today?"
        
        elif any(word in message_lower for word in ['help', 'what can you do', 'how does this work']):
            response = """I can help you with:
• Explaining complex concepts in simple terms
• Answering questions on various subjects (science, math, history, programming, etc.)
• Providing step-by-step explanations
• Helping with homework and learning materials
• Breaking down difficult topics
• Offering study tips and learning strategies

Just ask me anything you'd like to learn about!"""
        
        elif any(word in message_lower for word in ['teach', 'learn', 'explain', 'understand']):
            response = "I'd love to help you learn! What specific topic or concept would you like me to explain? I can break down complex ideas into easy-to-understand explanations."
        
        elif any(word in message_lower for word in ['python', 'javascript', 'programming', 'code', 'coding']):
            response = """I can help you with programming! Here are some topics I can assist with:

• Python: syntax, functions, data structures, OOP
• JavaScript: ES6+, async/await, DOM manipulation
• Web Development: HTML, CSS, frameworks
• Algorithms and data structures
• Best practices and coding patterns

What specific programming topic would you like to learn about?"""
        
        elif any(word in message_lower for word in ['math', 'mathematics', 'calculate', 'equation']):
            response = """I can help with mathematics! Topics include:

• Algebra and equations
• Calculus (derivatives, integrals)
• Geometry and trigonometry
• Statistics and probability
• Linear algebra
• Problem-solving strategies

What math concept would you like me to explain?"""
        
        elif any(word in message_lower for word in ['science', 'physics', 'chemistry', 'biology']):
            response = """I can explain science concepts! Areas I cover:

• Physics: mechanics, thermodynamics, electromagnetism
• Chemistry: atoms, molecules, reactions, periodic table
• Biology: cells, genetics, evolution, ecosystems
• Scientific method and experiments

Which scientific topic interests you?"""
        
        elif any(word in message_lower for word in ['history', 'historical', 'war', 'civilization']):
            response = "I can help you understand history! Whether it's ancient civilizations, world wars, cultural movements, or historical figures - I can provide detailed explanations and context. What historical topic would you like to explore?"
        
        elif '?' in message or any(word in message_lower for word in ['what', 'why', 'how', 'when', 'where', 'who']):
            # Extract key words from the question
            words = message_lower.split()
            key_words = [w for w in words if len(w) > 4 and w not in ['what', 'where', 'when', 'which', 'would', 'could', 'should', 'about']]
            
            if key_words:
                topic = ' '.join(key_words[:3])
                response = f"Great question about {topic}! While I'm currently running in basic mode, I can still provide helpful information. Let me help:\n\n"
                
                # Try to give a more intelligent response based on keywords
                if any(word in message_lower for word in ['quantum', 'physics', 'atom', 'particle']):
                    response += "Quantum physics deals with the behavior of matter and energy at atomic and subatomic scales. Key concepts include wave-particle duality, quantum entanglement, and the uncertainty principle. Would you like me to explain any specific aspect?"
                
                elif any(word in message_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'neural']):
                    response += "Artificial Intelligence involves creating systems that can perform tasks requiring human intelligence. Machine learning allows computers to learn from data without explicit programming. Key areas include supervised learning, neural networks, and deep learning. What aspect interests you most?"
                
                elif any(word in message_lower for word in ['web', 'website', 'html', 'css', 'frontend']):
                    response += "Web development involves creating websites using HTML (structure), CSS (styling), and JavaScript (interactivity). Modern web dev includes frameworks like React, Vue, or Angular for building dynamic applications. What would you like to know more about?"
                
                elif any(word in message_lower for word in ['function', 'variable', 'loop', 'array']):
                    response += "In programming, functions are reusable blocks of code, variables store data, loops repeat actions, and arrays hold collections of items. These are fundamental concepts in most programming languages. Which concept would you like me to explain in detail?"
                
                else:
                    response += "This is an interesting topic! Could you provide a bit more detail about what specific aspect you'd like to understand? The more specific your question, the better I can help you learn."
            else:
                response = "That's a great question! To give you the most helpful answer, could you provide a bit more context or specify what aspect you'd like to learn about?"
        
        else:
            # Default to being helpful and educational
            response = f"I see you're interested in learning about: '{message[:50]}...'\n\nLet me help you understand this better! Could you specify what particular aspect you'd like to learn? For example:\n\n• The basic concept or definition\n• How it works\n• Practical examples\n• Step-by-step explanation\n\nI'm here to make learning easier for you!"
        
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
