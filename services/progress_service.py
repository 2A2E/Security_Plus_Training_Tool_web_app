"""
Progress Tracking Service - Handles user progress tracking using Supabase
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

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

class ProgressService:
    """Service class for tracking user progress in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client for progress tracking"""
        config = Config()
        self.supabase_url = os.environ.get('SUPABASE_URL', config.SUPABASE_URL)
        self.supabase_key = os.environ.get('SUPABASE_KEY', config.SUPABASE_KEY)
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and API key are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("ProgressService initialized with Supabase")

    def _get_client(self, access_token: Optional[str] = None, refresh_token: Optional[str] = None) -> Client:
        """Return a Supabase client authenticated for the provided user session if available."""
        if access_token:
            client = create_client(self.supabase_url, self.supabase_key)
            try:
                if hasattr(client, 'postgrest'):
                    client.postgrest.auth(access_token)
                elif hasattr(client, 'rest'):
                    client.rest.auth(access_token)
            except Exception as e:
                logger.warning(f"Failed to authorize postgrest client with access token: {e}")
            try:
                client.auth.set_session(access_token, refresh_token)
            except Exception as e:
                logger.warning(f"Failed to set Supabase session with provided tokens: {e}")
            return client
        return self.client
    
    def save_quiz_result(self, user_id: str, quiz_result: Dict[str, Any], access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Save a quiz result to Supabase
        
        Args:
            user_id: User UUID
            quiz_result: Dict with quiz_id, quiz_type, section, score, total_questions, percentage, duration_seconds
            access_token: Optional access token to authenticate the request (for RLS)
        
        Returns:
            Dict with 'success' bool and 'message' or 'error'
        """
        try:
            # Use authenticated client for RLS - need both access_token and refresh_token
            client = self._get_client(access_token, refresh_token)
            
            data = {
                'user_id': user_id,
                'quiz_id': quiz_result.get('quiz_id', ''),
                'quiz_type': quiz_result.get('quiz_type', 'unknown'),
                'section': quiz_result.get('section'),
                'score': quiz_result.get('score', 0),
                'total_questions': quiz_result.get('total_questions', 0),
                'percentage': float(quiz_result.get('percentage', 0)),
                'duration_seconds': quiz_result.get('duration_seconds'),
                'completed_at': datetime.utcnow().isoformat()
            }
            
            result = client.table('user_quiz_results').insert(data).execute()
            
            if result.data:
                logger.info(f"Saved quiz result for user {user_id}: {quiz_result.get('quiz_type')}")
                return {
                    'success': True,
                    'message': 'Quiz result saved successfully',
                    'data': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save quiz result'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error saving quiz result: {error_msg}")
            return {
                'success': False,
                'error': f'Failed to save quiz result: {error_msg}'
            }
    
    def get_user_quiz_history(self, user_id: str, limit: int = 10, access_token: str = None, refresh_token: str = None) -> List[Dict[str, Any]]:
        """
        Get recent quiz results for a user
        
        Args:
            user_id: User UUID
            limit: Maximum number of results to return
        
        Returns:
            List of quiz result dictionaries
        """
        try:
            client = self._get_client(access_token, refresh_token)
            result = client.table('user_quiz_results')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('completed_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
        
        except Exception as e:
            logger.error(f"Error getting user quiz history: {e}")
            return []
    
    def get_user_statistics(self, user_id: str, access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Get aggregated statistics for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            Dict with total_quizzes, total_flashcards, total_practice_tests, average_score, total_study_time
        """
        try:
            # Get quiz results
            client = self._get_client(access_token, refresh_token)
            try:
                quiz_results = client.table('user_quiz_results')\
                    .select('*')\
                    .eq('user_id', user_id)\
                    .execute()
                quizzes = quiz_results.data if quiz_results.data else []
            except Exception as e:
                logger.warning(f"Error querying user_quiz_results table: {e}. Table may not exist yet.")
                quizzes = []
            
            # Calculate statistics
            total_quizzes = len([q for q in quizzes if q.get('quiz_type') != 'practice_test'])
            total_practice_tests = len([q for q in quizzes if q.get('quiz_type') == 'practice_test'])
            
            # Calculate average score
            scores = [q.get('percentage', 0) for q in quizzes if q.get('percentage') is not None]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # Get flashcard progress
            try:
                flashcard_results = client.table('user_flashcard_progress')\
                    .select('cards_viewed')\
                    .eq('user_id', user_id)\
                    .execute()
                flashcard_records = flashcard_results.data if flashcard_results.data else []
            except Exception as e:
                logger.warning(f"Error querying user_flashcard_progress table: {e}. Table may not exist yet.")
                flashcard_records = []
            
            total_flashcards = sum([f.get('cards_viewed', 0) for f in flashcard_records])
            
            # Get study time
            try:
                study_sessions = client.table('user_study_sessions')\
                    .select('duration_seconds')\
                    .eq('user_id', user_id)\
                    .execute()
                sessions = study_sessions.data if study_sessions.data else []
            except Exception as e:
                logger.warning(f"Error querying user_study_sessions table: {e}. Table may not exist yet.")
                sessions = []
            
            total_study_time = sum([s.get('duration_seconds', 0) for s in sessions])
            
            return {
                'total_quizzes': total_quizzes,
                'total_flashcards': total_flashcards,
                'total_practice_tests': total_practice_tests,
                'average_score': round(average_score, 2),
                'total_study_time_seconds': total_study_time,
                'total_study_time_hours': round(total_study_time / 3600, 2)
            }
        
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {
                'total_quizzes': 0,
                'total_flashcards': 0,
                'total_practice_tests': 0,
                'average_score': 0,
                'total_study_time_seconds': 0,
                'total_study_time_hours': 0
            }
    
    def get_section_progress(self, user_id: str, access_token: str = None, refresh_token: str = None) -> Dict[int, Dict[str, Any]]:
        """
        Get progress breakdown by section (1-5)
        
        Args:
            user_id: User UUID
        
        Returns:
            Dict mapping section number to progress data
        """
        try:
            # Get quiz results by section
            client = self._get_client(access_token, refresh_token)
            quiz_results = client.table('user_quiz_results')\
                .select('section, score, total_questions, percentage')\
                .eq('user_id', user_id)\
                .not_.is_('section', 'null')\
                .execute()
            
            quizzes = quiz_results.data if quiz_results.data else []
            
            # Get flashcard progress by section
            flashcard_results = client.table('user_flashcard_progress')\
                .select('section, cards_viewed')\
                .eq('user_id', user_id)\
                .execute()
            
            flashcards = flashcard_results.data if flashcard_results.data else []
            
            # Initialize section progress
            section_progress = {}
            for section in range(1, 6):
                section_quizzes = [q for q in quizzes if q.get('section') == section]
                section_flashcards = [f for f in flashcards if f.get('section') == section]
                
                section_scores = [q.get('percentage', 0) for q in section_quizzes if q.get('percentage') is not None]
                avg_score = sum(section_scores) / len(section_scores) if section_scores else 0
                
                section_progress[section] = {
                    'quizzes_completed': len(section_quizzes),
                    'flashcards_viewed': sum([f.get('cards_viewed', 0) for f in section_flashcards]),
                    'average_score': round(avg_score, 2),
                    'total_questions_answered': sum([q.get('total_questions', 0) for q in section_quizzes])
                }
            
            return section_progress
        
        except Exception as e:
            logger.error(f"Error getting section progress: {e}")
            return {}
    
    def get_study_time(self, user_id: str, days: int = 30, access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Get study time statistics
        
        Args:
            user_id: User UUID
            days: Number of days to look back
        
        Returns:
            Dict with total_time, daily_average, sessions_count
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            client = self._get_client(access_token, refresh_token)
            study_sessions = client.table('user_study_sessions')\
                .select('duration_seconds, started_at')\
                .eq('user_id', user_id)\
                .gte('started_at', cutoff_date)\
                .execute()
            
            sessions = study_sessions.data if study_sessions.data else []
            
            total_time = sum([s.get('duration_seconds', 0) for s in sessions])
            daily_average = total_time / days if days > 0 else 0
            
            return {
                'total_seconds': total_time,
                'total_hours': round(total_time / 3600, 2),
                'daily_average_seconds': round(daily_average, 2),
                'daily_average_hours': round(daily_average / 3600, 2),
                'sessions_count': len(sessions)
            }
        
        except Exception as e:
            logger.error(f"Error getting study time: {e}")
            return {
                'total_seconds': 0,
                'total_hours': 0,
                'daily_average_seconds': 0,
                'daily_average_hours': 0,
                'sessions_count': 0
            }
    
    def save_flashcard_progress(self, user_id: str, section: int, cards_viewed: int = 1, session_id: str = None, access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Save flashcard progress
        
        Args:
            user_id: User UUID
            section: Section number (1-5)
            cards_viewed: Number of cards viewed
            session_id: Optional session identifier
            access_token: Optional access token for authentication (for RLS)
            refresh_token: Optional refresh token (required if access_token is provided)
        
        Returns:
            Dict with 'success' bool and 'message' or 'error'
        """
        try:
            # Use authenticated client for RLS
            client = self._get_client(access_token, refresh_token)
            
            data = {
                'user_id': user_id,
                'section': section,
                'cards_viewed': cards_viewed,
                'session_id': session_id,
                'viewed_at': datetime.utcnow().isoformat()
            }
            
            result = client.table('user_flashcard_progress').insert(data).execute()
            
            if result.data:
                logger.info(f"Saved flashcard progress for user {user_id}, section {section}")
                return {
                    'success': True,
                    'message': 'Flashcard progress saved successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save flashcard progress'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error saving flashcard progress: {error_msg}")
            return {
                'success': False,
                'error': f'Failed to save flashcard progress: {error_msg}'
            }
    
    def save_study_session(self, user_id: str, session_type: str, duration_seconds: int, 
                          section: int = None, started_at: datetime = None, ended_at: datetime = None,
                          access_token: str = None, refresh_token: str = None) -> Dict[str, Any]:
        """
        Save a study session
        
        Args:
            user_id: User UUID
            session_type: Type of session ('quiz', 'flashcard', 'practice_test')
            duration_seconds: Duration in seconds
            section: Optional section number
            started_at: Optional start time (defaults to now - duration)
            ended_at: Optional end time (defaults to now)
            access_token: Optional access token for authentication (for RLS)
            refresh_token: Optional refresh token (required if access_token is provided)
        
        Returns:
            Dict with 'success' bool and 'message' or 'error'
        """
        try:
            # Use authenticated client for RLS
            client = self._get_client(access_token, refresh_token)
            
            if not ended_at:
                ended_at = datetime.utcnow()
            if not started_at:
                started_at = ended_at - timedelta(seconds=duration_seconds)
            
            data = {
                'user_id': user_id,
                'session_type': session_type,
                'section': section,
                'duration_seconds': duration_seconds,
                'started_at': started_at.isoformat(),
                'ended_at': ended_at.isoformat()
            }
            
            result = client.table('user_study_sessions').insert(data).execute()
            
            if result.data:
                logger.info(f"Saved study session for user {user_id}: {session_type}")
                return {
                    'success': True,
                    'message': 'Study session saved successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save study session'
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error saving study session: {error_msg}")
            return {
                'success': False,
                'error': f'Failed to save study session: {error_msg}'
            }
    
    def get_performance_trends(self, user_id: str, days: int = 30, access_token: str = None, refresh_token: str = None) -> List[Dict[str, Any]]:
        """
        Get performance trends over time
        
        Args:
            user_id: User UUID
            days: Number of days to look back
        
        Returns:
            List of performance data points
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            client = self._get_client(access_token, refresh_token)
            quiz_results = client.table('user_quiz_results')\
                .select('percentage, completed_at, quiz_type')\
                .eq('user_id', user_id)\
                .gte('completed_at', cutoff_date)\
                .order('completed_at', desc=False)\
                .execute()
            
            return quiz_results.data if quiz_results.data else []
        
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return []

# Global progress service instance
# Initialize with error handling in case tables don't exist yet
try:
    progress_service = ProgressService()
except Exception as e:
    logger.error(f"Failed to initialize ProgressService: {e}")
    logger.warning("Progress tracking will be disabled until database tables are created")
    # Create a dummy service that returns empty stats
    class DummyProgressService:
        def get_user_statistics(self, user_id, access_token=None, refresh_token=None):
            return {
                'total_quizzes': 0,
                'total_flashcards': 0,
                'total_practice_tests': 0,
                'average_score': 0,
                'total_study_time_seconds': 0,
                'total_study_time_hours': 0
            }
        def get_user_quiz_history(self, user_id, limit=10, access_token=None, refresh_token=None):
            return []
        def get_section_progress(self, user_id, access_token=None, refresh_token=None):
            return {}
        def get_study_time(self, user_id, days=30, access_token=None, refresh_token=None):
            return {
                'total_seconds': 0,
                'total_hours': 0,
                'daily_average_seconds': 0,
                'daily_average_hours': 0,
                'sessions_count': 0
            }
        def get_performance_trends(self, user_id, days=30, access_token=None, refresh_token=None):
            return []
        def save_quiz_result(self, user_id, quiz_result, access_token=None, refresh_token=None):
            return {'success': False, 'error': 'Database tables not initialized'}
        def save_flashcard_progress(self, user_id, section, cards_viewed=1, session_id=None, access_token=None, refresh_token=None):
            return {'success': False, 'error': 'Database tables not initialized'}
        def save_study_session(self, user_id, session_type, duration_seconds, section=None, started_at=None, ended_at=None, access_token=None, refresh_token=None):
            return {'success': False, 'error': 'Database tables not initialized'}
    progress_service = DummyProgressService()

