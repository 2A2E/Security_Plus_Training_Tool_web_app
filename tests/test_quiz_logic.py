"""
Unit tests for QuizSession and QuizManager classes
"""
import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from utils.quiz_logic import QuizSession, QuizManager


class TestQuizSession:
    """Test cases for QuizSession class"""
    
    def test_init(self):
        """Test QuizSession initialization"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        
        assert session.quiz_id == 'test_quiz_123'
        assert session.quiz_type == 'chapter_quiz'
        assert session.chapter == 1
        assert session.questions == []
        assert session.current_question_index == 0
        assert session.answers == []
        assert session.wrong_questions == []
        assert session.score == 0
        assert session.total_questions == 0
        assert session.completed is False
        assert isinstance(session.start_time, datetime)
    
    def test_add_questions(self, sample_questions):
        """Test adding questions to quiz session"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        
        assert session.questions == sample_questions
        assert session.total_questions == len(sample_questions)
    
    def test_get_current_question_valid_index(self, sample_questions):
        """Test getting current question with valid index"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 1
        
        result = session.get_current_question()
        
        assert result == sample_questions[1]
    
    def test_get_current_question_invalid_index(self, sample_questions):
        """Test getting current question with invalid index"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 10  # Out of bounds
        
        result = session.get_current_question()
        
        assert result is None
    
    def test_submit_answer_multiple_choice_correct(self, sample_questions):
        """Test submitting correct multiple choice answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 0  # Multiple choice question
        
        result = session.submit_answer('0', '1')
        
        assert result['is_correct'] is True
        assert result['score'] == 1
        assert result['total_questions'] == 3
        assert result['progress'] == (1 / 3) * 100
        assert result['wrong_questions_count'] == 0
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is True
    
    def test_submit_answer_multiple_choice_incorrect(self, sample_questions):
        """Test submitting incorrect multiple choice answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 0  # Multiple choice question
        
        result = session.submit_answer('2', '1')  # Wrong answer
        
        assert result['is_correct'] is False
        assert result['score'] == 0
        assert result['wrong_questions_count'] == 1
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is False
        assert 0 in session.wrong_questions
    
    def test_submit_answer_true_false_correct(self, sample_questions):
        """Test submitting correct true/false answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 1  # True/false question
        
        result = session.submit_answer('True', '2')
        
        assert result['is_correct'] is True
        assert result['score'] == 1
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is True
    
    def test_submit_answer_true_false_incorrect(self, sample_questions):
        """Test submitting incorrect true/false answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 1  # True/false question
        
        result = session.submit_answer('False', '2')  # Wrong answer
        
        assert result['is_correct'] is False
        assert result['score'] == 0
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is False
        assert 1 in session.wrong_questions
    
    def test_submit_answer_fill_in_blank_correct(self, sample_questions):
        """Test submitting correct fill-in-blank answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 2  # Fill-in-blank question
        
        result = session.submit_answer('Public Key Infrastructure', '3')
        
        assert result['is_correct'] is True
        assert result['score'] == 1
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is True
    
    def test_submit_answer_fill_in_blank_incorrect(self, sample_questions):
        """Test submitting incorrect fill-in-blank answer"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 2  # Fill-in-blank question
        
        result = session.submit_answer('Private Key Infrastructure', '3')  # Wrong answer
        
        assert result['is_correct'] is False
        assert result['score'] == 0
        assert len(session.answers) == 1
        assert session.answers[0]['is_correct'] is False
        assert 2 in session.wrong_questions
    
    def test_submit_answer_no_current_question(self):
        """Test submitting answer when no current question"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        # No questions added
        
        result = session.submit_answer('0', '1')
        
        assert result == {"error": "No current question"}
    
    def test_next_question_has_more(self, sample_questions):
        """Test moving to next question when more questions available"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 0
        
        result = session.next_question()
        
        assert result is True
        assert session.current_question_index == 1
    
    def test_next_question_no_more(self, sample_questions):
        """Test moving to next question when no more questions"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        session.current_question_index = 2  # Last question
        
        result = session.next_question()
        
        assert result is False
        assert session.current_question_index == 3
    
    def test_get_quiz_results(self, sample_questions):
        """Test getting quiz results"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        
        # Submit some answers
        session.current_question_index = 0
        session.submit_answer('0', '1')  # Correct
        session.current_question_index = 1
        session.submit_answer('False', '2')  # Incorrect
        session.current_question_index = 2
        session.submit_answer('Public Key Infrastructure', '3')  # Correct
        
        result = session.get_quiz_results()
        
        assert result['quiz_id'] == 'test_quiz_123'
        assert result['quiz_type'] == 'chapter_quiz'
        assert result['chapter'] == 1
        assert result['score'] == 2
        assert result['total_questions'] == 3
        assert result['percentage'] == round((2 / 3) * 100, 2)
        assert result['wrong_questions'] == 1
        assert result['wrong_question_indices'] == [1]
        assert len(result['answers']) == 3
        assert session.completed is True
        assert 'duration_seconds' in result
        assert 'start_time' in result
        assert 'end_time' in result
    
    def test_get_wrong_questions_for_review(self, sample_questions):
        """Test getting wrong questions for review"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        
        # Submit some answers
        session.current_question_index = 0
        session.submit_answer('0', '1')  # Correct
        session.current_question_index = 1
        session.submit_answer('False', '2')  # Incorrect
        session.current_question_index = 2
        session.submit_answer('Public Key Infrastructure', '3')  # Correct
        
        result = session.get_wrong_questions_for_review()
        
        assert len(result) == 1
        assert result[0]['id'] == '2'  # The wrong question
        assert result[0]['user_answer'] == 'False'
        assert result[0]['correct_answer'] == 'True'
        assert result[0]['is_correct'] is False
    
    def test_check_answer_multiple_choice_invalid_input(self, sample_questions):
        """Test checking multiple choice answer with invalid input"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        session.add_questions(sample_questions)
        
        # Test with non-numeric input
        is_correct, explanation = session._check_answer(sample_questions[0], 'invalid')
        
        assert is_correct is False
        assert explanation == sample_questions[0]['explanation']
    
    def test_get_correct_answer_multiple_choice(self, sample_questions):
        """Test getting correct answer for multiple choice question"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        
        result = session._get_correct_answer(sample_questions[0])
        
        assert result == 'A security device'  # First option
    
    def test_get_correct_answer_multiple_choice_invalid_index(self):
        """Test getting correct answer for multiple choice with invalid index"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        question = {
            'question_type': 'multiple_choice',
            'correct_answer': '10',  # Invalid index
            'options': ['Option A', 'Option B']
        }
        
        result = session._get_correct_answer(question)
        
        assert result == 'Option 10'  # Falls back to showing the index
    
    def test_get_correct_answer_true_false(self, sample_questions):
        """Test getting correct answer for true/false question"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        
        result = session._get_correct_answer(sample_questions[1])
        
        assert result == 'True'
    
    def test_get_correct_answer_fill_in_blank(self, sample_questions):
        """Test getting correct answer for fill-in-blank question"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        
        result = session._get_correct_answer(sample_questions[2])
        
        assert result == 'Public Key Infrastructure'  # First correct answer
    
    def test_get_correct_answer_fill_in_blank_json_string(self):
        """Test getting correct answer for fill-in-blank with JSON string"""
        session = QuizSession('test_quiz_123', 'chapter_quiz', 1)
        question = {
            'question_type': 'fill_in_blank',
            'correct_answers': '["Answer1", "Answer2"]'
        }
        
        result = session._get_correct_answer(question)
        
        assert result == 'Answer1'  # First answer from parsed JSON


class TestQuizManager:
    """Test cases for QuizManager class"""
    
    def test_init(self):
        """Test QuizManager initialization"""
        manager = QuizManager()
        
        assert manager.active_sessions == {}
    
    @patch('utils.quiz_logic.datetime')
    def test_create_quiz_session(self, mock_datetime):
        """Test creating a quiz session"""
        mock_datetime.utcnow.return_value.strftime.return_value = '20231201_120000'
        
        manager = QuizManager()
        quiz_id = manager.create_quiz_session('chapter_quiz', 1)
        
        assert quiz_id == 'chapter_quiz_1_20231201_120000'
        assert quiz_id in manager.active_sessions
        session = manager.active_sessions[quiz_id]
        assert session.quiz_id == quiz_id
        assert session.quiz_type == 'chapter_quiz'
        assert session.chapter == 1
    
    def test_get_session_existing(self):
        """Test getting an existing session"""
        manager = QuizManager()
        quiz_id = manager.create_quiz_session('chapter_quiz', 1)
        
        session = manager.get_session(quiz_id)
        
        assert session is not None
        assert session.quiz_id == quiz_id
    
    def test_get_session_nonexistent(self):
        """Test getting a non-existent session"""
        manager = QuizManager()
        
        session = manager.get_session('nonexistent_quiz')
        
        assert session is None
    
    def test_cleanup_session_existing(self):
        """Test cleaning up an existing session"""
        manager = QuizManager()
        quiz_id = manager.create_quiz_session('chapter_quiz', 1)
        
        assert quiz_id in manager.active_sessions
        manager.cleanup_session(quiz_id)
        assert quiz_id not in manager.active_sessions
    
    def test_cleanup_session_nonexistent(self):
        """Test cleaning up a non-existent session"""
        manager = QuizManager()
        
        # Should not raise an error
        manager.cleanup_session('nonexistent_quiz')
    
    def test_shuffle_questions(self, sample_questions):
        """Test shuffling questions"""
        manager = QuizManager()
        
        # Note: This test might be flaky due to randomness
        # In a real test, you might want to mock random.shuffle
        shuffled = manager.shuffle_questions(sample_questions)
        
        assert len(shuffled) == len(sample_questions)
        assert set(q['id'] for q in shuffled) == set(q['id'] for q in sample_questions)
    
    def test_filter_questions_by_difficulty(self, sample_questions):
        """Test filtering questions by difficulty"""
        manager = QuizManager()
        
        beginner_questions = manager.filter_questions_by_difficulty(sample_questions, 'beginner')
        
        assert len(beginner_questions) == 2  # Two beginner questions in sample
        assert all(q['difficulty'] == 'beginner' for q in beginner_questions)
    
    def test_filter_questions_by_difficulty_case_insensitive(self, sample_questions):
        """Test filtering questions by difficulty (case insensitive)"""
        manager = QuizManager()
        
        beginner_questions = manager.filter_questions_by_difficulty(sample_questions, 'BEGINNER')
        
        assert len(beginner_questions) == 2
        assert all(q['difficulty'] == 'beginner' for q in beginner_questions)
    
    def test_filter_questions_by_difficulty_no_matches(self, sample_questions):
        """Test filtering questions by difficulty with no matches"""
        manager = QuizManager()
        
        expert_questions = manager.filter_questions_by_difficulty(sample_questions, 'expert')
        
        assert len(expert_questions) == 0
