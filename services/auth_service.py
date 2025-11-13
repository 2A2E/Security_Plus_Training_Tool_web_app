"""
Authentication Service - Handles user authentication using Supabase Auth
"""
import os
import sys
import logging
from typing import Dict, Any, Optional
from functools import wraps

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    from config import Config
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    logging.error("Please install required dependencies: pip install supabase")
    raise

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service using Supabase Auth"""
    
    def __init__(self):
        """Initialize Supabase client for authentication"""
        config = Config()
        self.supabase_url = os.environ.get('SUPABASE_URL', config.SUPABASE_URL)
        self.supabase_key = os.environ.get('SUPABASE_KEY', config.SUPABASE_KEY)
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and API key are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("AuthService initialized with Supabase")
    
    def register_user(self, email: str, password: str, user_metadata: Dict[str, Any] = None, auto_confirm: bool = True) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth
        
        Args:
            email: User email address
            password: User password
            user_metadata: Optional metadata to store with user (first_name, last_name, etc.)
            auto_confirm: If True, attempt to auto-login after registration
        
        Returns:
            Dict with 'success' bool, 'message' or 'error', and optionally 'session' and 'user'
        """
        try:
            # Register user with Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            if response.user:
                logger.info(f"User registered successfully: {email}")
                
                # If auto_confirm is True and user is already confirmed (or confirmation disabled), try to login
                if auto_confirm and response.session:
                    return {
                        'success': True,
                        'message': 'Registration successful! Welcome to Security+ Exam Prep.',
                        'user': response.user,
                        'session': response.session
                    }
                else:
                    return {
                        'success': True,
                        'message': 'Registration successful! You can now login with your email and password.',
                        'user': response.user
                    }
            else:
                return {
                    'success': False,
                    'error': 'Registration failed. Please try again.'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Registration error: {error_msg}")
            
            # Handle common Supabase errors
            if 'already registered' in error_msg.lower() or 'already exists' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Email already registered. Please login instead.'
                }
            elif 'invalid' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Invalid email or password format.'
                }
            else:
                return {
                    'success': False,
                    'error': f'Registration failed: {error_msg}'
                }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Supabase Auth
        
        Args:
            email: User email address
            password: User password
        
        Returns:
            Dict with 'success' bool, 'session' (if successful), and 'message' or 'error'
        """
        try:
            # Authenticate user with Supabase Auth
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                logger.info(f"User logged in successfully: {email}")
                return {
                    'success': True,
                    'message': 'Login successful!',
                    'user': response.user,
                    'session': response.session
                }
            else:
                return {
                    'success': False,
                    'error': 'Login failed. Please check your credentials.'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Login error: {error_msg}")
            
            # Handle common Supabase errors
            if 'invalid' in error_msg.lower() or 'wrong' in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Invalid email or password. Please try again.'
                }
            elif 'not confirmed' in error_msg.lower() or 'email not verified' in error_msg.lower():
                # If email confirmation is required but user is trying to login, 
                # we'll allow them to login anyway by trying to resend confirmation
                # or just allow the login (if email confirmation is disabled in Supabase)
                return {
                    'success': False,
                    'error': 'Email verification may be required. Please check your email or contact support.'
                }
            else:
                return {
                    'success': False,
                    'error': f'Login failed: {error_msg}'
                }
    
    def logout_user(self, access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Sign out current user
        
        Args:
            access_token: Optional access token to sign out specific session
            refresh_token: Optional refresh token (required if access_token is provided)
        
        Returns:
            Dict with 'success' bool and 'message' or 'error'
        """
        try:
            # If we have tokens, create a client with that session and sign out
            if access_token and refresh_token:
                try:
                    client = create_client(self.supabase_url, self.supabase_key)
                    client.auth.set_session(access_token, refresh_token)
                    client.auth.sign_out()
                except Exception as e:
                    logger.warning(f"Could not sign out with tokens: {e}")
            else:
                # Sign out current session
                self.client.auth.sign_out()
            
            logger.info("User logged out successfully")
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Logout error: {error_msg}")
            # Still return success since we want to clear the session anyway
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
    
    def get_current_user(self, access_token: str = None) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user
        
        Args:
            access_token: Optional access token to get user info
        
        Returns:
            User dict if authenticated, None otherwise
        """
        try:
            # Note: Supabase Python client doesn't support setting session with just access_token
            # This method will work if the client was initialized with the session
            # For now, we'll use get_user() which relies on the client's internal state
            user = self.client.auth.get_user()
            
            if user and user.user:
                return {
                    'id': user.user.id,
                    'email': user.user.email,
                    'metadata': user.user.user_metadata or {},
                    'created_at': user.user.created_at,
                    'updated_at': user.user.updated_at
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def get_user_profile(self, user_id: str = None, access_token: str = None, refresh_token: str = None) -> Optional[Dict[str, Any]]:
        """
        Get user profile data
        
        Args:
            user_id: Optional user ID (currently not used, gets current user)
            access_token: Optional access token for authentication
            refresh_token: Optional refresh token (required if access_token is provided)
        
        Returns:
            User profile dict with metadata, None if not found
        """
        try:
            # Create a new client instance with session tokens if provided
            client = self.client
            if access_token and refresh_token:
                try:
                    # Create a new client instance for this request with the session
                    client = create_client(self.supabase_url, self.supabase_key)
                    client.auth.set_session(access_token, refresh_token)
                except Exception as e:
                    logger.warning(f"Could not set session, trying without: {e}")
                    # Fall back to default client
            
            # Get current user
            user_response = client.auth.get_user()
            
            if user_response and user_response.user:
                user = user_response.user
                metadata = user.user_metadata or {}
                # Convert datetime objects to ISO format strings for template compatibility
                created_at = user.created_at
                updated_at = user.updated_at
                if created_at and not isinstance(created_at, str):
                    created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
                if updated_at and not isinstance(updated_at, str):
                    updated_at = updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
                
                return {
                    'id': user.id,
                    'email': user.email,
                    'first_name': metadata.get('first_name', ''),
                    'last_name': metadata.get('last_name', ''),
                    'experience_level': metadata.get('experience_level', ''),
                    'interests': metadata.get('interests', ''),
                    'newsletter': metadata.get('newsletter', False),
                    'created_at': created_at,
                    'updated_at': updated_at
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def update_user_metadata(self, access_token: str = None, refresh_token: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update user metadata
        
        Args:
            access_token: User access token (optional if session exists)
            refresh_token: User refresh token (optional if session exists)
            metadata: Metadata to update
        
        Returns:
            Dict with 'success' bool and 'message' or 'error'
        """
        try:
            # Create a new client instance with session tokens if provided
            client = self.client
            if access_token and refresh_token:
                try:
                    # Create a new client instance for this request with the session
                    client = create_client(self.supabase_url, self.supabase_key)
                    client.auth.set_session(access_token, refresh_token)
                except Exception as e:
                    logger.warning(f"Could not set session, trying without: {e}")
                    # Fall back to default client
            
            # Update user metadata
            response = client.auth.update_user({
                "data": metadata
            })
            
            if response.user:
                logger.info(f"User metadata updated for: {response.user.email}")
                return {
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': response.user
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update profile'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error updating user metadata: {error_msg}")
            return {
                'success': False,
                'error': f'Failed to update profile: {error_msg}'
            }

# Global auth service instance
auth_service = AuthService()

# Helper decorator for protecting routes
def login_required(f):
    """
    Decorator to require authentication for a route
    Usage: @login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect, url_for, flash
        
        # Check if user is authenticated
        if 'user_id' not in session or 'access_token' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function

