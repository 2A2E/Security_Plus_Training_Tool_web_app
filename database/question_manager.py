"""
Question manager for Supabase database operations
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class QuestionManager:
    """Manager for question-related Supabase database operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.questions_table = db_manager.get_table('questions')
        logger.info("QuestionManager initialized with Supabase")
    
    def add_question(self, question_data: Dict[str, Any]) -> str:
        """
        Add a new question to the database
        
        Args:
            question_data: Dictionary containing question information
            
        Returns:
            str: The ID of the inserted question
        """
        try:
            # Add metadata
            question_data['created_at'] = datetime.utcnow().isoformat()
            question_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Convert lists to JSON strings for storage
            if 'options' in question_data and isinstance(question_data['options'], list):
                question_data['options'] = json.dumps(question_data['options'])
            if 'tags' in question_data and isinstance(question_data['tags'], list):
                question_data['tags'] = json.dumps(question_data['tags'])
            if 'correct_answers' in question_data and isinstance(question_data['correct_answers'], list):
                question_data['correct_answers'] = json.dumps(question_data['correct_answers'])
            
            result = self.questions_table.insert(question_data).execute()
            
            if result.data and len(result.data) > 0:
                question_id = str(result.data[0]['id'])
                logger.info(f"Question added with ID: {question_id}")
                return question_id
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            logger.error(f"Error adding question: {e}")
            raise
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a question by ID
        
        Args:
            question_id: The ID of the question
            
        Returns:
            Dict containing question data or None if not found
        """
        try:
            result = self.questions_table.select('*').eq('id', question_id).execute()
            
            if result.data and len(result.data) > 0:
                question = result.data[0]
                # Parse JSON fields back to Python objects
                if question.get('options'):
                    question['options'] = json.loads(question['options'])
                if question.get('tags'):
                    question['tags'] = json.loads(question['tags'])
                if question.get('correct_answers'):
                    question['correct_answers'] = json.loads(question['correct_answers'])
                return question
            return None
            
        except Exception as e:
            logger.error(f"Error getting question {question_id}: {e}")
            return None
    
    def get_questions(self, 
                     category: str = None, 
                     difficulty: str = None, 
                     tags: List[str] = None,
                     limit: int = 50,
                     skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get questions with optional filtering
        
        Args:
            category: Filter by category
            difficulty: Filter by difficulty level
            tags: Filter by tags (any match)
            limit: Maximum number of questions to return
            skip: Number of questions to skip (for pagination)
            
        Returns:
            List of question dictionaries
        """
        try:
            query = self.questions_table.select('*')
            
            # Apply filters
            if category:
                query = query.eq('category', category)
            if difficulty:
                query = query.eq('difficulty', difficulty)
            
            # Apply pagination
            query = query.range(skip, skip + limit - 1)
            
            # Order by created_at descending
            query = query.order('created_at', desc=True)
            
            result = query.execute()
            
            questions = []
            if result.data:
                for question in result.data:
                    # Parse JSON fields back to Python objects
                    if question.get('options'):
                        question['options'] = json.loads(question['options'])
                    if question.get('tags'):
                        question['tags'] = json.loads(question['tags'])
                    if question.get('correct_answers'):
                        question['correct_answers'] = json.loads(question['correct_answers'])
                    questions.append(question)
            
            # Filter by tags if specified (PostgreSQL JSON operations)
            if tags and questions:
                filtered_questions = []
                for question in questions:
                    question_tags = question.get('tags', [])
                    if any(tag in question_tags for tag in tags):
                        filtered_questions.append(question)
                questions = filtered_questions
            
            return questions
            
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []
    
    def update_question(self, question_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a question
        
        Args:
            question_id: The ID of the question to update
            update_data: Dictionary containing fields to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Convert lists to JSON strings for storage
            if 'options' in update_data and isinstance(update_data['options'], list):
                update_data['options'] = json.dumps(update_data['options'])
            if 'tags' in update_data and isinstance(update_data['tags'], list):
                update_data['tags'] = json.dumps(update_data['tags'])
            if 'correct_answers' in update_data and isinstance(update_data['correct_answers'], list):
                update_data['correct_answers'] = json.dumps(update_data['correct_answers'])
            
            result = self.questions_table.update(update_data).eq('id', question_id).execute()
            
            return result.data is not None and len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating question {question_id}: {e}")
            return False
    
    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question
        
        Args:
            question_id: The ID of the question to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            result = self.questions_table.delete().eq('id', question_id).execute()
            return result.data is not None and len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting question {question_id}: {e}")
            return False
    
    def get_question_categories(self) -> List[str]:
        """Get all unique question categories"""
        try:
            result = self.questions_table.select('category').execute()
            
            if result.data:
                categories = list(set([q['category'] for q in result.data if q.get('category')]))
                return sorted(categories)
            return []
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_question_tags(self) -> List[str]:
        """Get all unique question tags"""
        try:
            result = self.questions_table.select('tags').execute()
            
            if result.data:
                all_tags = set()
                for question in result.data:
                    if question.get('tags'):
                        try:
                            tags = json.loads(question['tags'])
                            if isinstance(tags, list):
                                all_tags.update(tags)
                        except json.JSONDecodeError:
                            continue
                return sorted(list(all_tags))
            return []
            
        except Exception as e:
            logger.error(f"Error getting tags: {e}")
            return []
    
    def get_question_count(self, category: str = None, difficulty: str = None) -> int:
        """Get total count of questions with optional filtering"""
        try:
            query = self.questions_table.select('id', count='exact')
            
            if category:
                query = query.eq('category', category)
            if difficulty:
                query = query.eq('difficulty', difficulty)
            
            result = query.execute()
            return result.count if result.count is not None else 0
            
        except Exception as e:
            logger.error(f"Error getting question count: {e}")
            return 0

# Global question manager instance
try:
    from .connection import db_manager
    question_manager = QuestionManager(db_manager)
except ImportError as e:
    logger.error(f"Could not import db_manager: {e}")
    question_manager = None