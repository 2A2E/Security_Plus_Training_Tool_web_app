"""
Quiz Logic Module - Handles quiz state, scoring, and question management
"""
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuizSession:
    """Manages a quiz session with state, scoring, and question tracking"""
    
    def __init__(self, quiz_id: str, quiz_type: str, chapter: Optional[int] = None):
        self.quiz_id = quiz_id
        self.quiz_type = quiz_type
        self.chapter = chapter
        self.questions: List[Dict[str, Any]] = []
        self.current_question_index = 0
        self.answers: List[Dict[str, Any]] = []
        self.wrong_questions: List[int] = []  # Indices of wrong questions
        self.start_time = datetime.utcnow()
        self.score = 0
        self.total_questions = 0
        self.completed = False
        
    def add_questions(self, questions: List[Dict[str, Any]]):
        """Add questions to the quiz session"""
        self.questions = questions
        self.total_questions = len(questions)
        logger.info(f"Added {len(questions)} questions to quiz session {self.quiz_id}")
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question"""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def submit_answer(self, answer: str, question_id: str) -> Dict[str, Any]:
        """Submit an answer and return result"""
        current_question = self.get_current_question()
        if not current_question:
            return {"error": "No current question"}
        
        # Parse the answer based on question type
        is_correct, explanation = self._check_answer(current_question, answer)
        
        # Store the answer
        answer_data = {
            "question_id": question_id,
            "question_index": self.current_question_index,
            "user_answer": answer,
            "correct_answer": self._get_correct_answer(current_question),
            "is_correct": is_correct,
            "submitted_at": datetime.utcnow().isoformat()
        }
        self.answers.append(answer_data)
        
        # Track wrong questions for review
        if not is_correct:
            self.wrong_questions.append(self.current_question_index)
        
        # Update score
        if is_correct:
            self.score += 1
        
        result = {
            "is_correct": is_correct,
            "explanation": explanation,
            "correct_answer": self._get_correct_answer(current_question),
            "user_answer": answer,
            "score": self.score,
            "total_questions": self.total_questions,
            "progress": (len(self.answers) / self.total_questions) * 100,
            "wrong_questions_count": len(self.wrong_questions)
        }
        
        return result
    
    def next_question(self) -> bool:
        """Move to next question, return True if more questions available"""
        self.current_question_index += 1
        return self.current_question_index < len(self.questions)
    
    def get_quiz_results(self) -> Dict[str, Any]:
        """Get final quiz results"""
        if not self.completed:
            self.completed = True
        
        percentage = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            "quiz_id": self.quiz_id,
            "quiz_type": self.quiz_type,
            "chapter": self.chapter,
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": round(percentage, 2),
            "wrong_questions": len(self.wrong_questions),
            "duration_seconds": round(duration, 2),
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "answers": self.answers,
            "wrong_question_indices": self.wrong_questions
        }
    
    def get_wrong_questions_for_review(self) -> List[Dict[str, Any]]:
        """Get questions that were answered incorrectly for review"""
        wrong_questions = []
        for index in self.wrong_questions:
            if index < len(self.questions):
                question = self.questions[index].copy()
                # Add the user's answer and correct answer
                answer_data = next((a for a in self.answers if a["question_index"] == index), None)
                if answer_data:
                    question["user_answer"] = answer_data["user_answer"]
                    question["correct_answer"] = answer_data["correct_answer"]
                    question["is_correct"] = answer_data["is_correct"]
                wrong_questions.append(question)
        return wrong_questions
    
    def _check_answer(self, question: Dict[str, Any], user_answer: str) -> Tuple[bool, str]:
        """Check if the user's answer is correct"""
        question_type = question.get('question_type', '')
        explanation = question.get('explanation', 'No explanation available.')
        
        if question_type == 'multiple_choice':
            # For multiple choice, correct_answer is the index (0-based)
            correct_answer = question.get('correct_answer', '0')
            try:
                user_index = int(user_answer)
                is_correct = str(user_index) == str(correct_answer)
            except ValueError:
                is_correct = False
        
        elif question_type == 'true_false':
            correct_answer = question.get('correct_answer', 'True')
            is_correct = user_answer.lower() == str(correct_answer).lower()
        
        elif question_type == 'fill_in_blank':
            # For fill-in-blank, check against correct_answers array
            correct_answers = question.get('correct_answers', [])
            if isinstance(correct_answers, str):
                try:
                    correct_answers = json.loads(correct_answers)
                except json.JSONDecodeError:
                    correct_answers = [correct_answers]
            
            user_answer_clean = user_answer.strip().lower()
            is_correct = any(user_answer_clean == ans.strip().lower() for ans in correct_answers)
        
        else:
            is_correct = False
        
        return is_correct, explanation
    
    def _get_correct_answer(self, question: Dict[str, Any]) -> str:
        """Get the correct answer for display"""
        question_type = question.get('question_type', '')
        
        if question_type == 'multiple_choice':
            correct_index = question.get('correct_answer', '0')
            options = question.get('options', [])
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except json.JSONDecodeError:
                    options = []
            
            try:
                index = int(correct_index)
                if 0 <= index < len(options):
                    return options[index]
            except (ValueError, IndexError):
                pass
            return f"Option {correct_index}"
        
        elif question_type == 'true_false':
            return str(question.get('correct_answer', 'True'))
        
        elif question_type == 'fill_in_blank':
            correct_answers = question.get('correct_answers', [])
            if isinstance(correct_answers, str):
                try:
                    correct_answers = json.loads(correct_answers)
                except json.JSONDecodeError:
                    correct_answers = [correct_answers]
            
            if correct_answers:
                return correct_answers[0]  # Return first correct answer
            return str(question.get('correct_answer', ''))
        
        return str(question.get('correct_answer', ''))

class QuizManager:
    """Manages quiz sessions and provides quiz-related utilities"""
    
    def __init__(self):
        self.active_sessions: Dict[str, QuizSession] = {}
    
    def create_quiz_session(self, quiz_type: str, chapter: Optional[int] = None) -> str:
        """Create a new quiz session and return session ID"""
        quiz_id = f"{quiz_type}_{chapter}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        session = QuizSession(quiz_id, quiz_type, chapter)
        self.active_sessions[quiz_id] = session
        logger.info(f"Created quiz session: {quiz_id}")
        return quiz_id
    
    def get_session(self, quiz_id: str) -> Optional[QuizSession]:
        """Get a quiz session by ID"""
        return self.active_sessions.get(quiz_id)
    
    def cleanup_session(self, quiz_id: str):
        """Remove a quiz session"""
        if quiz_id in self.active_sessions:
            del self.active_sessions[quiz_id]
            logger.info(f"Cleaned up quiz session: {quiz_id}")
    
    def shuffle_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Shuffle questions while maintaining their original order for reference"""
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def filter_questions_by_difficulty(self, questions: List[Dict[str, Any]], difficulty: str) -> List[Dict[str, Any]]:
        """Filter questions by difficulty level"""
        return [q for q in questions if q.get('difficulty', '').lower() == difficulty.lower()]

# Global quiz manager instance
quiz_manager = QuizManager()
