"""
Unit tests for QuizService class
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from services.quiz_service import QuizService


class TestQuizService:
    """Test cases for QuizService class"""
    
    def test_init(self):
        """Test QuizService initialization"""
        service = QuizService()
        assert service.question_manager is not None
    
    @patch('services.quiz_service.question_manager')
    @patch('services.quiz_service.quiz_manager')
    def test_create_chapter_quiz_success(self, mock_quiz_manager, mock_question_manager, sample_questions):
        """Test successful chapter quiz creation"""
        # Setup mocks
        mock_question_manager.get_questions.return_value = sample_questions[:2]
        mock_quiz_manager.create_quiz_session.return_value = 'test_quiz_123'
        mock_session = Mock()
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.create_chapter_quiz(chapter=1, limit=10)
        
        # Assertions
        assert result == 'test_quiz_123'
        mock_question_manager.get_questions.assert_called_once_with(
            category='Technologies and Tools', limit=10
        )
        mock_quiz_manager.create_quiz_session.assert_called_once_with('chapter_quiz', 1)
        mock_session.add_questions.assert_called_once()
    
    @patch('services.quiz_service.question_manager')
    def test_create_chapter_quiz_no_questions(self, mock_question_manager):
        """Test chapter quiz creation when no questions are found"""
        # Setup mocks
        mock_question_manager.get_questions.return_value = []
        
        # Create service and test
        service = QuizService()
        result = service.create_chapter_quiz(chapter=1, limit=10)
        
        # Assertions
        assert result is None
        mock_question_manager.get_questions.assert_called_once_with(
            category='Technologies and Tools', limit=10
        )
    
    @patch('services.quiz_service.question_manager')
    @patch('services.quiz_service.quiz_manager')
    def test_create_chapter_quiz_exception(self, mock_quiz_manager, mock_question_manager):
        """Test chapter quiz creation with exception"""
        # Setup mocks
        mock_question_manager.get_questions.side_effect = Exception("Database error")
        
        # Create service and test
        service = QuizService()
        result = service.create_chapter_quiz(chapter=1, limit=10)
        
        # Assertions
        assert result is None
    
    @patch('services.quiz_service.question_manager')
    @patch('services.quiz_service.quiz_manager')
    def test_create_random_quiz_success(self, mock_quiz_manager, mock_question_manager, sample_questions):
        """Test successful random quiz creation"""
        # Setup mocks
        mock_question_manager.get_questions.return_value = sample_questions
        mock_quiz_manager.shuffle_questions.return_value = sample_questions
        mock_quiz_manager.create_quiz_session.return_value = 'test_quiz_456'
        mock_session = Mock()
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.create_random_quiz(limit=10)
        
        # Assertions
        assert result == 'test_quiz_456'
        mock_question_manager.get_questions.assert_called_once_with(limit=10)
        mock_quiz_manager.shuffle_questions.assert_called_once_with(sample_questions)
        mock_quiz_manager.create_quiz_session.assert_called_once_with('random_quiz')
        mock_session.add_questions.assert_called_once()
    
    @patch('services.quiz_service.question_manager')
    def test_create_random_quiz_no_questions(self, mock_question_manager):
        """Test random quiz creation when no questions are found"""
        # Setup mocks
        mock_question_manager.get_questions.return_value = []
        
        # Create service and test
        service = QuizService()
        result = service.create_random_quiz(limit=10)
        
        # Assertions
        assert result is None
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_quiz_question_success(self, mock_quiz_manager, sample_questions):
        """Test successful quiz question retrieval"""
        # Setup mocks
        mock_session = Mock()
        mock_session.current_question_index = 0
        mock_session.total_questions = 3
        mock_session.get_current_question.return_value = sample_questions[0]
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.get_quiz_question('test_quiz_123', 1)
        
        # Assertions
        assert result is not None
        assert result['quiz_id'] == 'test_quiz_123'
        assert result['question_number'] == 1
        assert result['total_questions'] == 3
        assert result['progress_percentage'] == (1 / 3) * 100
        mock_session.get_current_question.assert_called_once()
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_quiz_question_session_not_found(self, mock_quiz_manager):
        """Test quiz question retrieval when session not found"""
        # Setup mocks
        mock_quiz_manager.get_session.return_value = None
        
        # Create service and test
        service = QuizService()
        result = service.get_quiz_question('invalid_quiz', 1)
        
        # Assertions
        assert result is None
    
    @patch('services.quiz_service.quiz_manager')
    def test_submit_quiz_answer_success(self, mock_quiz_manager, sample_questions):
        """Test successful quiz answer submission"""
        # Setup mocks
        mock_session = Mock()
        mock_session.current_question_index = 0
        mock_session.total_questions = 3
        mock_session.get_current_question.return_value = sample_questions[0]
        mock_session.submit_answer.return_value = {
            'is_correct': True,
            'explanation': 'Correct answer',
            'score': 1
        }
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.submit_quiz_answer('test_quiz_123', '0')
        
        # Assertions
        assert result is not None
        assert result['is_correct'] is True
        assert result['question_number'] == 1
        assert result['total_questions'] == 3
        assert result['has_next_question'] is True
        assert result['quiz_completed'] is False
        mock_session.submit_answer.assert_called_once_with('0', '1')
    
    @patch('services.quiz_service.quiz_manager')
    def test_submit_quiz_answer_quiz_completed(self, mock_quiz_manager, sample_questions):
        """Test quiz answer submission when quiz is completed"""
        # Setup mocks
        mock_session = Mock()
        mock_session.current_question_index = 2  # Last question
        mock_session.total_questions = 3
        mock_session.get_current_question.return_value = sample_questions[0]
        mock_session.submit_answer.return_value = {
            'is_correct': True,
            'explanation': 'Correct answer',
            'score': 3
        }
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.submit_quiz_answer('test_quiz_123', '0')
        
        # Assertions
        assert result is not None
        assert result['quiz_completed'] is True
        assert result['has_next_question'] is False
    
    @patch('services.quiz_service.quiz_manager')
    def test_submit_quiz_answer_session_not_found(self, mock_quiz_manager):
        """Test quiz answer submission when session not found"""
        # Setup mocks
        mock_quiz_manager.get_session.return_value = None
        
        # Create service and test
        service = QuizService()
        result = service.submit_quiz_answer('invalid_quiz', '0')
        
        # Assertions
        assert result is None
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_quiz_results_success(self, mock_quiz_manager):
        """Test successful quiz results retrieval"""
        # Setup mocks
        mock_session = Mock()
        mock_session.get_quiz_results.return_value = {
            'quiz_id': 'test_quiz_123',
            'score': 8,
            'total_questions': 10,
            'percentage': 80.0
        }
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.get_quiz_results('test_quiz_123')
        
        # Assertions
        assert result is not None
        assert result['score'] == 8
        assert result['percentage'] == 80.0
        mock_session.get_quiz_results.assert_called_once()
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_quiz_results_session_not_found(self, mock_quiz_manager):
        """Test quiz results retrieval when session not found"""
        # Setup mocks
        mock_quiz_manager.get_session.return_value = None
        
        # Create service and test
        service = QuizService()
        result = service.get_quiz_results('invalid_quiz')
        
        # Assertions
        assert result is None
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_wrong_questions_review_success(self, mock_quiz_manager):
        """Test successful wrong questions review retrieval"""
        # Setup mocks
        wrong_questions = [
            {'id': '1', 'question_text': 'Question 1', 'user_answer': 'A', 'correct_answer': 'B'},
            {'id': '2', 'question_text': 'Question 2', 'user_answer': 'C', 'correct_answer': 'D'}
        ]
        mock_session = Mock()
        mock_session.get_wrong_questions_for_review.return_value = wrong_questions
        mock_quiz_manager.get_session.return_value = mock_session
        
        # Create service and test
        service = QuizService()
        result = service.get_wrong_questions_review('test_quiz_123')
        
        # Assertions
        assert result == wrong_questions
        assert len(result) == 2
        mock_session.get_wrong_questions_for_review.assert_called_once()
    
    @patch('services.quiz_service.quiz_manager')
    def test_get_wrong_questions_review_session_not_found(self, mock_quiz_manager):
        """Test wrong questions review when session not found"""
        # Setup mocks
        mock_quiz_manager.get_session.return_value = None
        
        # Create service and test
        service = QuizService()
        result = service.get_wrong_questions_review('invalid_quiz')
        
        # Assertions
        assert result == []
    
    @patch('services.quiz_service.quiz_manager')
    def test_cleanup_quiz_session(self, mock_quiz_manager):
        """Test quiz session cleanup"""
        # Create service and test
        service = QuizService()
        service.cleanup_quiz_session('test_quiz_123')
        
        # Assertions
        mock_quiz_manager.cleanup_session.assert_called_once_with('test_quiz_123')
    
    def test_parse_question_json_fields(self, sample_questions):
        """Test parsing of JSON fields in questions"""
        # Create questions with JSON strings
        questions_with_json = [
            {
                'id': '1',
                'question_text': 'Test question',
                'options': '["Option A", "Option B", "Option C"]',
                'tags': '["tag1", "tag2"]',
                'correct_answers': '["Answer1", "Answer2"]'
            }
        ]
        
        # Create service and test
        service = QuizService()
        result = service._parse_question_json_fields(questions_with_json)
        
        # Assertions
        assert result[0]['options'] == ["Option A", "Option B", "Option C"]
        assert result[0]['tags'] == ["tag1", "tag2"]
        assert result[0]['correct_answers'] == ["Answer1", "Answer2"]
    
    def test_parse_question_json_fields_invalid_json(self):
        """Test parsing of invalid JSON fields in questions"""
        # Create questions with invalid JSON strings
        questions_with_invalid_json = [
            {
                'id': '1',
                'question_text': 'Test question',
                'options': 'invalid json',
                'tags': 'invalid json',
                'correct_answers': 'invalid json'
            }
        ]
        
        # Create service and test
        service = QuizService()
        result = service._parse_question_json_fields(questions_with_invalid_json)
        
        # Assertions
        assert result[0]['options'] == []
        assert result[0]['tags'] == []
        assert result[0]['correct_answers'] == ['invalid json']  # Falls back to original string
    
    def test_parse_question_json_fields_already_parsed(self):
        """Test parsing when JSON fields are already parsed"""
        # Create questions with already parsed JSON
        questions_already_parsed = [
            {
                'id': '1',
                'question_text': 'Test question',
                'options': ['Option A', 'Option B'],
                'tags': ['tag1', 'tag2'],
                'correct_answers': ['Answer1']
            }
        ]
        
        # Create service and test
        service = QuizService()
        result = service._parse_question_json_fields(questions_already_parsed)
        
        # Assertions
        assert result[0]['options'] == ['Option A', 'Option B']
        assert result[0]['tags'] == ['tag1', 'tag2']
        assert result[0]['correct_answers'] == ['Answer1']
