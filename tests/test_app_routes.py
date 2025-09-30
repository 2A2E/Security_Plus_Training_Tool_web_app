"""
Unit tests for Flask app routes
"""
import pytest
import json
from unittest.mock import Mock, patch
from flask import session, url_for


class TestAppRoutes:
    """Test cases for Flask app routes"""
    
    def test_home_route(self, client):
        """Test home page route"""
        response = client.get('/')
        
        assert response.status_code == 200
        # Check if the template is rendered (basic check)
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_about_route(self, client):
        """Test about page route"""
        response = client.get('/about')
        
        assert response.status_code == 200
    
    def test_contact_route(self, client):
        """Test contact page route"""
        response = client.get('/contact')
        
        assert response.status_code == 200
    
    def test_training_route(self, client):
        """Test training page route"""
        response = client.get('/training')
        
        assert response.status_code == 200
    
    def test_flashcards_route(self, client):
        """Test flashcards page route"""
        response = client.get('/flashcards')
        
        assert response.status_code == 200
    
    def test_quizzes_route(self, client):
        """Test quizzes page route"""
        response = client.get('/quizzes')
        
        assert response.status_code == 200
    
    def test_practice_test_route(self, client):
        """Test practice test page route"""
        response = client.get('/practice-test')
        
        assert response.status_code == 200
    
    @patch('main_app.quiz_service')
    def test_quiz_chapter_success(self, mock_quiz_service, client, sample_questions):
        """Test successful chapter quiz creation"""
        mock_quiz_service.create_chapter_quiz.return_value = 'test_quiz_123'
        mock_quiz_service.get_quiz_question.return_value = {
            'id': '1',
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'options': ['A security device', 'A network protocol'],
            'correct_answer': '0',
            'explanation': 'A firewall is a security device.',
            'question_number': 1,
            'total_questions': 10,
            'progress_percentage': 10.0
        }
        
        response = client.get('/quiz/chapter/1')
        
        assert response.status_code == 200
        mock_quiz_service.create_chapter_quiz.assert_called_once_with(chapter=1, limit=10)
        mock_quiz_service.get_quiz_question.assert_called_once_with('test_quiz_123', 1)
    
    @patch('main_app.quiz_service')
    def test_quiz_chapter_no_questions(self, mock_quiz_service, client):
        """Test chapter quiz when no questions found"""
        mock_quiz_service.create_chapter_quiz.return_value = None
        
        response = client.get('/quiz/chapter/1')
        
        assert response.status_code == 302  # Redirect
        # Should redirect to quizzes page
        assert '/quizzes' in response.location
    
    @patch('main_app.quiz_service')
    def test_quiz_chapter_error_loading_questions(self, mock_quiz_service, client):
        """Test chapter quiz when error loading questions"""
        mock_quiz_service.create_chapter_quiz.return_value = 'test_quiz_123'
        mock_quiz_service.get_quiz_question.return_value = None
        
        response = client.get('/quiz/chapter/1')
        
        assert response.status_code == 302  # Redirect
        # Should redirect to quizzes page
        assert '/quizzes' in response.location
    
    @patch('main_app.quiz_service')
    def test_quiz_random_success(self, mock_quiz_service, client):
        """Test successful random quiz creation"""
        mock_quiz_service.create_random_quiz.return_value = 'test_quiz_456'
        mock_quiz_service.get_quiz_question.return_value = {
            'id': '2',
            'question_text': 'Is encryption important?',
            'question_type': 'true_false',
            'correct_answer': 'True',
            'explanation': 'Yes, encryption is important.',
            'question_number': 1,
            'total_questions': 10,
            'progress_percentage': 10.0
        }
        
        response = client.get('/quiz/random')
        
        assert response.status_code == 200
        mock_quiz_service.create_random_quiz.assert_called_once_with(limit=10)
        mock_quiz_service.get_quiz_question.assert_called_once_with('test_quiz_456', 1)
    
    @patch('main_app.quiz_service')
    def test_quiz_random_no_questions(self, mock_quiz_service, client):
        """Test random quiz when no questions found"""
        mock_quiz_service.create_random_quiz.return_value = None
        
        response = client.get('/quiz/random')
        
        assert response.status_code == 302  # Redirect
        # Should redirect to quizzes page
        assert '/quizzes' in response.location
    
    @patch('main_app.quiz_service')
    def test_quiz_question_success(self, mock_quiz_service, client):
        """Test successful quiz question retrieval"""
        mock_quiz_service.get_quiz_question.return_value = {
            'id': '1',
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'options': ['A security device', 'A network protocol'],
            'correct_answer': '0',
            'explanation': 'A firewall is a security device.',
            'question_number': 2,
            'total_questions': 10,
            'progress_percentage': 20.0
        }
        
        response = client.get('/quiz/test_quiz_123/question/2')
        
        assert response.status_code == 200
        mock_quiz_service.get_quiz_question.assert_called_once_with('test_quiz_123', 2)
    
    @patch('main_app.quiz_service')
    def test_quiz_question_not_found(self, mock_quiz_service, client):
        """Test quiz question when question not found"""
        mock_quiz_service.get_quiz_question.return_value = None
        
        response = client.get('/quiz/test_quiz_123/question/2')
        
        assert response.status_code == 302  # Redirect
        # Should redirect to quizzes page
        assert '/quizzes' in response.location
    
    @patch('main_app.quiz_service')
    def test_submit_quiz_answer_success(self, mock_quiz_service, client):
        """Test successful quiz answer submission"""
        mock_quiz_service.submit_quiz_answer.return_value = {
            'is_correct': True,
            'explanation': 'Correct answer',
            'question_number': 1,
            'total_questions': 10,
            'has_next_question': True,
            'quiz_completed': False
        }
        
        response = client.post('/quiz/test_quiz_123/submit', data={'answer': '0'})
        
        assert response.status_code == 302  # Redirect to next question
        mock_quiz_service.submit_quiz_answer.assert_called_once_with('test_quiz_123', '0')
    
    @patch('main_app.quiz_service')
    def test_submit_quiz_answer_quiz_completed(self, mock_quiz_service, client):
        """Test quiz answer submission when quiz is completed"""
        mock_quiz_service.submit_quiz_answer.return_value = {
            'is_correct': True,
            'explanation': 'Correct answer',
            'question_number': 10,
            'total_questions': 10,
            'has_next_question': False,
            'quiz_completed': True
        }
        
        response = client.post('/quiz/test_quiz_123/submit', data={'answer': '0'})
        
        assert response.status_code == 302  # Redirect to results
        # Should redirect to quiz results
        assert '/quiz/test_quiz_123/results' in response.location
    
    def test_submit_quiz_answer_no_answer(self, client):
        """Test quiz answer submission with no answer"""
        response = client.post('/quiz/test_quiz_123/submit', data={})
        
        assert response.status_code == 302  # Redirect back
    
    @patch('main_app.quiz_service')
    def test_submit_quiz_answer_error(self, mock_quiz_service, client):
        """Test quiz answer submission with error"""
        mock_quiz_service.submit_quiz_answer.return_value = None
        
        response = client.post('/quiz/test_quiz_123/submit', data={'answer': '0'})
        
        assert response.status_code == 302  # Redirect to quizzes
        assert '/quizzes' in response.location
    
    @patch('main_app.quiz_service')
    def test_quiz_results_success(self, mock_quiz_service, client):
        """Test successful quiz results display"""
        mock_quiz_service.get_quiz_results.return_value = {
            'quiz_id': 'test_quiz_123',
            'score': 8,
            'total_questions': 10,
            'percentage': 80.0,
            'wrong_questions': 2
        }
        mock_quiz_service.get_wrong_questions_review.return_value = [
            {'id': '1', 'question_text': 'Question 1', 'user_answer': 'A', 'correct_answer': 'B'},
            {'id': '2', 'question_text': 'Question 2', 'user_answer': 'C', 'correct_answer': 'D'}
        ]
        
        response = client.get('/quiz/test_quiz_123/results')
        
        assert response.status_code == 200
        mock_quiz_service.get_quiz_results.assert_called_once_with('test_quiz_123')
        mock_quiz_service.get_wrong_questions_review.assert_called_once_with('test_quiz_123')
    
    @patch('main_app.quiz_service')
    def test_quiz_results_not_found(self, mock_quiz_service, client):
        """Test quiz results when results not found"""
        mock_quiz_service.get_quiz_results.return_value = None
        
        response = client.get('/quiz/test_quiz_123/results')
        
        assert response.status_code == 302  # Redirect to quizzes
        assert '/quizzes' in response.location
    
    def test_login_get(self, client):
        """Test login page GET request"""
        response = client.get('/login')
        
        assert response.status_code == 200
    
    def test_login_post_success(self, client):
        """Test successful login POST request"""
        # First register a user
        client.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'experience_level': 'beginner',
            'interests': 'security',
            'terms': 'on'
        })
        
        # Then login
        response = client.post('/login', data={
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 302  # Redirect to home
        assert '/' in response.location
    
    def test_login_post_invalid_credentials(self, client):
        """Test login POST with invalid credentials"""
        response = client.post('/login', data={
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200  # Stay on login page
        # Should show error message
    
    def test_register_get(self, client):
        """Test register page GET request"""
        response = client.get('/register')
        
        assert response.status_code == 200
    
    def test_register_post_success(self, client):
        """Test successful registration POST request"""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'experience_level': 'intermediate',
            'interests': 'cryptography',
            'terms': 'on'
        })
        
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location
    
    def test_register_post_missing_fields(self, client):
        """Test registration POST with missing required fields"""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            # Missing experience_level, interests, terms
        })
        
        assert response.status_code == 200  # Stay on register page
        # Should show error message
    
    def test_register_post_password_mismatch(self, client):
        """Test registration POST with password mismatch"""
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword',
            'experience_level': 'intermediate',
            'interests': 'cryptography',
            'terms': 'on'
        })
        
        assert response.status_code == 200  # Stay on register page
        # Should show error message
    
    def test_register_post_duplicate_email(self, client):
        """Test registration POST with duplicate email"""
        # First registration
        client.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'experience_level': 'beginner',
            'interests': 'security',
            'terms': 'on'
        })
        
        # Second registration with same email
        response = client.post('/register', data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'password': 'password456',
            'confirm_password': 'password456',
            'experience_level': 'intermediate',
            'interests': 'cryptography',
            'terms': 'on'
        })
        
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location
    
    def test_logout(self, client):
        """Test logout route"""
        # First login to set session
        client.post('/register', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'experience_level': 'beginner',
            'interests': 'security',
            'terms': 'on'
        })
        
        client.post('/login', data={
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout')
        
        assert response.status_code == 302  # Redirect to home
        assert '/' in response.location
    
    def test_invalid_route(self, client):
        """Test accessing invalid route"""
        response = client.get('/invalid-route')
        
        assert response.status_code == 404
    
    def test_app_configuration(self, app):
        """Test Flask app configuration"""
        assert app.config['SECRET_KEY'] == 'test-secret-key'
        assert 'question_api' in [bp.name for bp in app.blueprints.values()]
    
    def test_route_registration(self, app):
        """Test that all routes are properly registered"""
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        # Check main routes
        assert '/' in rules
        assert '/about' in rules
        assert '/contact' in rules
        assert '/training' in rules
        assert '/flashcards' in rules
        assert '/quizzes' in rules
        assert '/practice-test' in rules
        assert '/login' in rules
        assert '/register' in rules
        assert '/logout' in rules
        
        # Check quiz routes
        assert '/quiz/chapter/<int:chapter>' in rules
        assert '/quiz/random' in rules
        assert '/quiz/<quiz_id>/question/<int:question_number>' in rules
        assert '/quiz/<quiz_id>/submit' in rules
        assert '/quiz/<quiz_id>/results' in rules
