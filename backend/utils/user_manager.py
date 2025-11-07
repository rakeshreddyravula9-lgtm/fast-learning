import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

class UserManager:
    """
    Manages user registration, authentication, and session handling
    """
    
    def __init__(self, users_dir='backend/users'):
        self.users_dir = users_dir
        self.users_file = os.path.join(users_dir, 'users.json')
        self.sessions_file = os.path.join(users_dir, 'sessions.json')
        os.makedirs(users_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, {})
        if not os.path.exists(self.sessions_file):
            self._save_json(self.sessions_file, {})
    
    def _save_json(self, filepath: str, data: dict):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_json(self, filepath: str) -> dict:
        """Load data from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = uuid.uuid4().hex
        
        # Use SHA-256 for password hashing
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed, salt
    
    def register_user(self, username: str, email: str, password: str, full_name: str = '') -> Dict:
        """Register a new user"""
        users = self._load_json(self.users_file)
        
        # Check if username or email already exists
        for user_id, user_data in users.items():
            if user_data['username'].lower() == username.lower():
                return {'success': False, 'error': 'Username already exists'}
            if user_data['email'].lower() == email.lower():
                return {'success': False, 'error': 'Email already exists'}
        
        # Validate inputs
        if len(username) < 3:
            return {'success': False, 'error': 'Username must be at least 3 characters'}
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}
        if '@' not in email:
            return {'success': False, 'error': 'Invalid email address'}
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash, salt = self._hash_password(password)
        
        users[user_id] = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'password_hash': password_hash,
            'salt': salt,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True
        }
        
        self._save_json(self.users_file, users)
        
        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name
        }
    
    def authenticate_user(self, username_or_email: str, password: str) -> Dict:
        """Authenticate user with username/email and password"""
        users = self._load_json(self.users_file)
        
        # Find user by username or email
        user_data = None
        for uid, data in users.items():
            if (data['username'].lower() == username_or_email.lower() or 
                data['email'].lower() == username_or_email.lower()):
                user_data = data
                break
        
        if not user_data:
            return {'success': False, 'error': 'Invalid username/email or password'}
        
        if not user_data.get('is_active', True):
            return {'success': False, 'error': 'Account is inactive'}
        
        # Verify password
        password_hash, _ = self._hash_password(password, user_data['salt'])
        
        if password_hash != user_data['password_hash']:
            return {'success': False, 'error': 'Invalid username/email or password'}
        
        # Update last login
        user_data['last_login'] = datetime.now().isoformat()
        users[user_data['user_id']] = user_data
        self._save_json(self.users_file, users)
        
        # Create session
        session_token = self._create_session(user_data['user_id'])
        
        return {
            'success': True,
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data.get('full_name', ''),
            'session_token': session_token
        }
    
    def _create_session(self, user_id: str, expires_in_days: int = 7) -> str:
        """Create a new session for user"""
        sessions = self._load_json(self.sessions_file)
        
        session_token = str(uuid.uuid4())
        expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        sessions[session_token] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at
        }
        
        self._save_json(self.sessions_file, sessions)
        return session_token
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """Verify session token and return user data"""
        if not session_token:
            return None
        
        sessions = self._load_json(self.sessions_file)
        
        if session_token not in sessions:
            return None
        
        session = sessions[session_token]
        
        # Check if session expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            # Remove expired session
            del sessions[session_token]
            self._save_json(self.sessions_file, sessions)
            return None
        
        # Get user data
        users = self._load_json(self.users_file)
        user_id = session['user_id']
        
        if user_id not in users:
            return None
        
        user_data = users[user_id]
        
        return {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data.get('full_name', ''),
            'created_at': user_data['created_at'],
            'last_login': user_data.get('last_login')
        }
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session"""
        sessions = self._load_json(self.sessions_file)
        
        if session_token in sessions:
            del sessions[session_token]
            self._save_json(self.sessions_file, sessions)
            return True
        
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user data by user ID"""
        users = self._load_json(self.users_file)
        
        if user_id not in users:
            return None
        
        user_data = users[user_id]
        
        return {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data.get('full_name', ''),
            'created_at': user_data['created_at'],
            'last_login': user_data.get('last_login')
        }
    
    def update_user_profile(self, user_id: str, full_name: str = None, email: str = None) -> Dict:
        """Update user profile information"""
        users = self._load_json(self.users_file)
        
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user_data = users[user_id]
        
        if full_name is not None:
            user_data['full_name'] = full_name
        
        if email is not None:
            # Check if email already used by another user
            for uid, data in users.items():
                if uid != user_id and data['email'].lower() == email.lower():
                    return {'success': False, 'error': 'Email already in use'}
            user_data['email'] = email
        
        users[user_id] = user_data
        self._save_json(self.users_file, users)
        
        return {'success': True, 'message': 'Profile updated successfully'}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict:
        """Change user password"""
        users = self._load_json(self.users_file)
        
        if user_id not in users:
            return {'success': False, 'error': 'User not found'}
        
        user_data = users[user_id]
        
        # Verify old password
        old_hash, _ = self._hash_password(old_password, user_data['salt'])
        if old_hash != user_data['password_hash']:
            return {'success': False, 'error': 'Current password is incorrect'}
        
        # Validate new password
        if len(new_password) < 6:
            return {'success': False, 'error': 'New password must be at least 6 characters'}
        
        # Hash new password
        new_hash, new_salt = self._hash_password(new_password)
        user_data['password_hash'] = new_hash
        user_data['salt'] = new_salt
        
        users[user_id] = user_data
        self._save_json(self.users_file, users)
        
        return {'success': True, 'message': 'Password changed successfully'}
