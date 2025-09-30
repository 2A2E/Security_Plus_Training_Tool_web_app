"""
Pytest configuration and fixtures for Security Plus Training Tool tests
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_question_manager():
    """Mock question manager for testing"""
    mock_manager = Mock()
    mock_manager.get_questions.return_value = [
        {
            'id': '1',
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'category': 'Technologies and Tools',
            'difficulty': 'beginner',
            'options': ['A security device', 'A network protocol', 'A type of virus', 'A database'],
            'correct_answer': '0',
            'explanation': 'A firewall is a security device that monitors and controls network traffic.',
            'tags': ['firewall', 'security', 'network']
        },
        {
            'id': '2',
            'question_text': 'Is encryption important for data security?',
            'question_type': 'true_false',
            'category': 'Cryptography and PKI',
            'difficulty': 'beginner',
            'correct_answer': 'True',
            'explanation': 'Encryption is essential for protecting data confidentiality.',
            'tags': ['encryption', 'security']
        }
    ]
    mock_manager.get_question.return_value = {
        'id': '1',
        'question_text': 'What is a firewall?',
        'question_type': 'multiple_choice',
        'category': 'Technologies and Tools',
        'difficulty': 'beginner',
        'options': ['A security device', 'A network protocol', 'A type of virus', 'A database'],
        'correct_answer': '0',
        'explanation': 'A firewall is a security device that monitors and controls network traffic.',
        'tags': ['firewall', 'security', 'network']
    }
    mock_manager.get_question_categories.return_value = [
        'Technologies and Tools',
        'Threats, Attacks, and Vulnerabilities',
        'Identity and Access Management',
        'Cryptography and PKI'
    ]
    mock_manager.get_question_tags.return_value = [
        'firewall', 'security', 'network', 'encryption', 'authentication'
    ]
    mock_manager.get_question_count.return_value = 10
    return mock_manager

@pytest.fixture
def sample_questions():
    """Sample questions for testing"""
    return [
        {
            'id': '1',
            'question_text': 'What is a firewall?',
            'question_type': 'multiple_choice',
            'category': 'Technologies and Tools',
            'difficulty': 'beginner',
            'options': ['A security device', 'A network protocol', 'A type of virus', 'A database'],
            'correct_answer': '0',
            'explanation': 'A firewall is a security device that monitors and controls network traffic.',
            'tags': ['firewall', 'security', 'network']
        },
        {
            'id': '2',
            'question_text': 'Is encryption important for data security?',
            'question_type': 'true_false',
            'category': 'Cryptography and PKI',
            'difficulty': 'beginner',
            'correct_answer': 'True',
            'explanation': 'Encryption is essential for protecting data confidentiality.',
            'tags': ['encryption', 'security']
        },
        {
            'id': '3',
            'question_text': 'What does PKI stand for?',
            'question_type': 'fill_in_blank',
            'category': 'Cryptography and PKI',
            'difficulty': 'intermediate',
            'correct_answers': ['Public Key Infrastructure'],
            'explanation': 'PKI stands for Public Key Infrastructure.',
            'tags': ['pki', 'cryptography']
        }
    ]

@pytest.fixture
def mock_quiz_session():
    """Mock quiz session for testing"""
    session = Mock()
    session.quiz_id = 'test_quiz_123'
    session.quiz_type = 'chapter_quiz'
    session.chapter = 1
    session.questions = []
    session.current_question_index = 0
    session.answers = []
    session.wrong_questions = []
    session.start_time = datetime.utcnow()
    session.score = 0
    session.total_questions = 0
    session.completed = False
    
    session.add_questions = Mock()
    session.get_current_question = Mock()
    session.submit_answer = Mock()
    session.next_question = Mock()
    session.get_quiz_results = Mock()
    session.get_wrong_questions_for_review = Mock()
    
    return session

@pytest.fixture
def mock_quiz_manager():
    """Mock quiz manager for testing"""
    manager = Mock()
    manager.active_sessions = {}
    manager.create_quiz_session = Mock(return_value='test_quiz_123')
    manager.get_session = Mock()
    manager.cleanup_session = Mock()
    manager.shuffle_questions = Mock(side_effect=lambda x: x)
    manager.filter_questions_by_difficulty = Mock(side_effect=lambda x, y: x)
    
    return manager

@pytest.fixture
def app():
    """Flask app fixture for testing"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import the main app.py file directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_app", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
    main_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_app)
    
    flask_app = main_app.app
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    return flask_app

@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Flask CLI test runner"""
    return app.test_cli_runner()
