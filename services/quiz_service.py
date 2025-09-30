"""
Quiz Service - Handles quiz operations and database interactions
"""
import json
from typing import List, Dict, Any, Optional
from database.question_manager import question_manager
from utils.quiz_logic import quiz_manager, QuizSession
import logging

logger = logging.getLogger(__name__)

class QuizService:
    """Service class for quiz operations"""
    
    def __init__(self):
        self.question_manager = question_manager
    
    def create_chapter_quiz(self, chapter: int, limit: int = 10) -> Optional[str]:
        """Create a quiz for a specific chapter"""
        try:
            # Map chapter to category
            chapter_categories = {
                1: 'Technologies and Tools',
                2: 'Threats, Attacks, and Vulnerabilities', 
                3: 'Identity and Access Management',
                4: 'Cryptography and PKI',
                5: 'Technologies and Tools'
            }
            
            category = chapter_categories.get(chapter, 'Technologies and Tools')
            
            # Get questions for this chapter
            questions = self.question_manager.get_questions(category=category, limit=limit)
            
            if not questions:
                logger.warning(f"No questions found for chapter {chapter} (category: {category})")
                return None
            
            # Parse JSON fields in questions
            questions = self._parse_question_json_fields(questions)
            
            # Create quiz session
            quiz_id = quiz_manager.create_quiz_session('chapter_quiz', chapter)
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(questions)
            
            logger.info(f"Created chapter quiz for chapter {chapter} with {len(questions)} questions")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating chapter quiz: {e}")
            return None
    
    def create_random_quiz(self, limit: int = 10) -> Optional[str]:
        """Create a random quiz from all categories"""
        try:
            # Get random questions from all categories
            questions = self.question_manager.get_questions(limit=limit)
            
            if not questions:
                logger.warning("No questions found for random quiz")
                return None
            
            # Parse JSON fields in questions
            questions = self._parse_question_json_fields(questions)
            
            # Shuffle questions
            questions = quiz_manager.shuffle_questions(questions)
            
            # Create quiz session
            quiz_id = quiz_manager.create_quiz_session('random_quiz')
            session = quiz_manager.get_session(quiz_id)
            session.add_questions(questions)
            
            logger.info(f"Created random quiz with {len(questions)} questions")
            return quiz_id
            
        except Exception as e:
            logger.error(f"Error creating random quiz: {e}")
            return None
    
    def get_quiz_question(self, quiz_id: str, question_number: int = 1) -> Optional[Dict[str, Any]]:
        """Get a specific question from a quiz session"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            # Set current question index (0-based)
            session.current_question_index = question_number - 1
            
            question = session.get_current_question()
            if question:
                # Add quiz metadata
                question['quiz_id'] = quiz_id
                question['question_number'] = question_number
                question['total_questions'] = session.total_questions
                question['progress_percentage'] = (question_number / session.total_questions) * 100
                
            return question
            
        except Exception as e:
            logger.error(f"Error getting quiz question: {e}")
            return None
    
    def submit_quiz_answer(self, quiz_id: str, answer: str) -> Optional[Dict[str, Any]]:
        """Submit an answer for the current question"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            current_question = session.get_current_question()
            if not current_question:
                logger.error(f"No current question in session: {quiz_id}")
                return None
            
            # Submit the answer
            result = session.submit_answer(answer, str(current_question.get('id', '')))
            
            # Add additional metadata
            result['question_number'] = session.current_question_index + 1
            result['total_questions'] = session.total_questions
            result['has_next_question'] = session.current_question_index + 1 < session.total_questions
            result['quiz_completed'] = session.current_question_index + 1 >= session.total_questions
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting quiz answer: {e}")
            return None
    
    def get_quiz_results(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get final quiz results"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return None
            
            return session.get_quiz_results()
            
        except Exception as e:
            logger.error(f"Error getting quiz results: {e}")
            return None
    
    def get_wrong_questions_review(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get questions that were answered incorrectly for review"""
        try:
            session = quiz_manager.get_session(quiz_id)
            if not session:
                logger.error(f"Quiz session not found: {quiz_id}")
                return []
            
            return session.get_wrong_questions_for_review()
            
        except Exception as e:
            logger.error(f"Error getting wrong questions review: {e}")
            return []
    
    def cleanup_quiz_session(self, quiz_id: str):
        """Clean up a quiz session"""
        quiz_manager.cleanup_session(quiz_id)
    
    def _parse_question_json_fields(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse JSON fields in questions"""
        for question in questions:
            # Parse options
            if question.get('options'):
                if isinstance(question['options'], str):
                    try:
                        question['options'] = json.loads(question['options'])
                    except json.JSONDecodeError:
                        question['options'] = []
            
            # Parse tags
            if question.get('tags'):
                if isinstance(question['tags'], str):
                    try:
                        question['tags'] = json.loads(question['tags'])
                    except json.JSONDecodeError:
                        question['tags'] = []
            
            # Parse correct_answers
            if question.get('correct_answers'):
                if isinstance(question['correct_answers'], str):
                    try:
                        question['correct_answers'] = json.loads(question['correct_answers'])
                    except json.JSONDecodeError:
                        question['correct_answers'] = [question['correct_answers']]
        
        return questions

# Global quiz service instance
quiz_service = QuizService()
