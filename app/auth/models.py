import hashlib
from datetime import datetime

class User:
    """User model for authentication"""
    
    # Mock database - in production, use a real database
    _users = {}
    _next_id = 1
    
    def __init__(self, id, first_name, last_name, email, password_hash, 
                 experience_level, interests, newsletter, created_at=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.experience_level = experience_level
        self.interests = interests
        self.newsletter = newsletter
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def create(cls, first_name, last_name, email, password, 
               experience_level, interests, newsletter=False):
        """Create a new user"""
        user_id = cls._next_id
        cls._next_id += 1
        
        password_hash = cls._hash_password(password)
        
        user = cls(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            experience_level=experience_level,
            interests=interests,
            newsletter=newsletter
        )
        
        cls._users[user_id] = user
        return user
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        return cls._users.get(user_id)
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        for user in cls._users.values():
            if user.email == email:
                return user
        return None
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256 (in production, use bcrypt)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'experience_level': self.experience_level,
            'interests': self.interests,
            'newsletter': self.newsletter,
            'created_at': self.created_at.isoformat()
        }
