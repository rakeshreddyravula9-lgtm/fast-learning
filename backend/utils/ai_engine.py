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
        
        # Simple pattern matching
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey']):
            response = "Hello! I'm an AI assistant. How can I help you today?"
        
        elif any(word in message_lower for word in ['how are you', 'how do you do']):
            response = "I'm functioning well, thank you! I'm here to help you with any questions or tasks you have."
        
        elif any(word in message_lower for word in ['your name', 'who are you']):
            response = "I'm an AI assistant powered by this chatbot platform. I'm here to help answer your questions and assist with various tasks."
        
        elif any(word in message_lower for word in ['help', 'what can you do']):
            response = """I can help you with:
• Answering questions on various topics
• Providing information and explanations
• Assisting with problem-solving
• Having conversations
• And much more! Just ask me anything."""
        
        elif '?' in message:
            response = f"That's an interesting question about '{message[:50]}...'. While I'm currently running in basic mode, I'd be happy to discuss this topic with you. Could you provide more context?"
        
        else:
            response = "I understand. Could you tell me more about what you'd like to know or discuss? I'm here to help!"
        
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
