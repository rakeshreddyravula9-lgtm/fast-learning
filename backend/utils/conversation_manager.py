import os
import json
from datetime import datetime
from typing import Dict, List
import uuid

class ConversationManager:
    """
    Manages conversation storage and retrieval
    Stores conversations in JSON files
    """
    
    def __init__(self, storage_dir='backend/conversations'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # In-memory cache for active conversations
        self.active_conversations = {}
    
    def get_conversation(self, session_id: str) -> Dict:
        """Get or create a conversation"""
        # Check cache first
        if session_id in self.active_conversations:
            return self.active_conversations[session_id]
        
        # Check file system
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                conversation = json.load(f)
                self.active_conversations[session_id] = conversation
                return conversation
        
        # Create new conversation
        conversation = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'messages': [],
            'title': 'New Conversation',
            'metadata': {}
        }
        
        self.active_conversations[session_id] = conversation
        self._save_conversation(session_id, conversation)
        
        return conversation
    
    def add_message(self, session_id: str, message: Dict):
        """Add a message to a conversation"""
        conversation = self.get_conversation(session_id)
        
        conversation['messages'].append(message)
        conversation['updated_at'] = datetime.now().isoformat()
        
        # Update title based on first user message
        if len(conversation['messages']) == 1 and message['role'] == 'user':
            # Use first 50 characters of first message as title
            conversation['title'] = message['content'][:50] + ('...' if len(message['content']) > 50 else '')
        
        self.active_conversations[session_id] = conversation
        self._save_conversation(session_id, conversation)
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations (metadata only)"""
        conversations = []
        
        # Get all JSON files in storage directory
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            conversation = json.load(f)
                            # Return metadata only
                            conversations.append({
                                'session_id': conversation['session_id'],
                                'title': conversation['title'],
                                'created_at': conversation['created_at'],
                                'updated_at': conversation['updated_at'],
                                'message_count': len(conversation['messages'])
                            })
                    except Exception as e:
                        print(f"Error loading conversation {filename}: {e}")
        
        # Sort by updated_at (most recent first)
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return conversations
    
    def delete_conversation(self, session_id: str):
        """Delete a conversation"""
        # Remove from cache
        if session_id in self.active_conversations:
            del self.active_conversations[session_id]
        
        # Remove file
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def clear_all(self):
        """Clear all conversations"""
        # Clear cache
        self.active_conversations = {}
        
        # Remove all files
        if os.path.exists(self.storage_dir):
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    os.remove(filepath)
    
    def _save_conversation(self, session_id: str, conversation: Dict):
        """Save conversation to file"""
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(conversation, f, indent=2)
    
    def export_conversation(self, session_id: str, format='json') -> str:
        """Export conversation in different formats"""
        conversation = self.get_conversation(session_id)
        
        if format == 'json':
            return json.dumps(conversation, indent=2)
        
        elif format == 'text':
            text = f"Conversation: {conversation['title']}\n"
            text += f"Created: {conversation['created_at']}\n"
            text += "=" * 50 + "\n\n"
            
            for msg in conversation['messages']:
                role = "You" if msg['role'] == 'user' else "AI"
                text += f"{role}: {msg['content']}\n\n"
            
            return text
        
        elif format == 'markdown':
            md = f"# {conversation['title']}\n\n"
            md += f"**Created:** {conversation['created_at']}\n\n"
            md += "---\n\n"
            
            for msg in conversation['messages']:
                role = "**You**" if msg['role'] == 'user' else "**AI**"
                md += f"{role}: {msg['content']}\n\n"
            
            return md
        
        else:
            return json.dumps(conversation, indent=2)
