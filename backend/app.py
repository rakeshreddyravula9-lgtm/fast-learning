from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
from datetime import datetime
import uuid

# Import AI utilities
from utils.ai_engine import AIEngine
from utils.conversation_manager import ConversationManager

app = Flask(__name__, static_folder='../frontend')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize AI Engine and Conversation Manager
ai_engine = AIEngine()
conversation_manager = ConversationManager()

# Store active connections
active_sessions = {}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_engine': 'ready'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message and get AI response"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        model = data.get('model', 'gpt-3.5-turbo')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create conversation
        conversation = conversation_manager.get_conversation(session_id)
        
        # Add user message to conversation
        conversation_manager.add_message(session_id, {
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate AI response
        ai_response = ai_engine.generate_response(
            message=user_message,
            conversation_history=conversation['messages'],
            model=model
        )
        
        # Add AI response to conversation
        conversation_manager.add_message(session_id, {
            'role': 'assistant',
            'content': ai_response['content'],
            'timestamp': datetime.now().isoformat(),
            'model': model
        })
        
        return jsonify({
            'session_id': session_id,
            'response': ai_response['content'],
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'tokens_used': ai_response.get('tokens_used', 0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = conversation_manager.get_all_conversations()
        return jsonify({
            'conversations': conversations,
            'count': len(conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get a specific conversation"""
    try:
        conversation = conversation_manager.get_conversation(session_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify(conversation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<session_id>', methods=['DELETE'])
def delete_conversation(session_id):
    """Delete a conversation"""
    try:
        conversation_manager.delete_conversation(session_id)
        return jsonify({'message': 'Conversation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/clear', methods=['POST'])
def clear_conversations():
    """Clear all conversations"""
    try:
        conversation_manager.clear_all()
        return jsonify({'message': 'All conversations cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    return jsonify({
        'models': [
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI'},
            {'id': 'gpt-4', 'name': 'GPT-4', 'provider': 'OpenAI'},
            {'id': 'local-llama', 'name': 'Local LLaMA', 'provider': 'Hugging Face'},
            {'id': 'local-mistral', 'name': 'Local Mistral', 'provider': 'Hugging Face'}
        ]
    })

# WebSocket Events for Real-time Chat
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    session_id = request.sid
    active_sessions[session_id] = {
        'connected_at': datetime.now().isoformat()
    }
    emit('connected', {'session_id': session_id})
    print(f"Client connected: {session_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    if session_id in active_sessions:
        del active_sessions[session_id]
    print(f"Client disconnected: {session_id}")

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming message via WebSocket"""
    try:
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Get conversation
        conversation = conversation_manager.get_conversation(session_id)
        
        # Add user message
        conversation_manager.add_message(session_id, {
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Emit typing indicator
        emit('typing', {'is_typing': True})
        
        # Generate AI response with streaming
        ai_response = ai_engine.generate_response(
            message=user_message,
            conversation_history=conversation['messages'],
            model=model,
            stream=True
        )
        
        # Stream response back to client
        full_response = ""
        for chunk in ai_response['chunks']:
            full_response += chunk
            emit('message_chunk', {
                'chunk': chunk,
                'session_id': session_id
            })
        
        # Add AI response to conversation
        conversation_manager.add_message(session_id, {
            'role': 'assistant',
            'content': full_response,
            'timestamp': datetime.now().isoformat(),
            'model': model
        })
        
        # Emit completion
        emit('typing', {'is_typing': False})
        emit('message_complete', {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('new_conversation')
def handle_new_conversation():
    """Create a new conversation"""
    session_id = str(uuid.uuid4())
    conversation = conversation_manager.get_conversation(session_id)
    emit('conversation_created', {
        'session_id': session_id,
        'conversation': conversation
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('backend/conversations', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Run the app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
