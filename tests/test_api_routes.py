"""
Unit tests for API routes
"""
import pytest
import json
from unittest.mock import Mock, patch
from api.question_routes import question_api


class TestQuestionAPIRoutes:
    """Test cases for question API routes"""
    
    def test_get_questions_success(self, client, mock_question_manager, sample_questions):
        """Test successful GET /api/questions"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_questions.return_value = sample_questions[:2]
            
            response = client.get('/api/questions')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['questions']) == 2
            assert data['count'] == 2
            mock_question_manager.get_questions.assert_called_once_with(
                category=None,
                difficulty=None,
                tags=None,
                limit=10,
                skip=0
            )
    
    def test_get_questions_with_filters(self, client, mock_question_manager, sample_questions):
        """Test GET /api/questions with query parameters"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_questions.return_value = sample_questions[:1]
            
            response = client.get('/api/questions?category=Technologies%20and%20Tools&difficulty=beginner&limit=5&skip=2')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            mock_question_manager.get_questions.assert_called_once_with(
                category='Technologies and Tools',
                difficulty='beginner',
                tags=None,
                limit=5,
                skip=2
            )
    
    def test_get_questions_with_tags(self, client, mock_question_manager, sample_questions):
        """Test GET /api/questions with multiple tags"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_questions.return_value = sample_questions[:1]
            
            response = client.get('/api/questions?tags=firewall&tags=security')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            mock_question_manager.get_questions.assert_called_once_with(
                category=None,
                difficulty=None,
                tags=['firewall', 'security'],
                limit=10,
                skip=0
            )
    
    def test_get_questions_no_question_manager(self, client):
        """Test GET /api/questions when question_manager is None"""
        with patch('api.question_routes.question_manager', None):
            response = client.get('/api/questions')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database not configured' in data['error']
    
    def test_get_questions_exception(self, client, mock_question_manager):
        """Test GET /api/questions with exception"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_questions.side_effect = Exception("Database error")
            
            response = client.get('/api/questions')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Database error"
    
    def test_get_question_success(self, client, mock_question_manager):
        """Test successful GET /api/questions/<question_id>"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question.return_value = {
                'id': '1',
                'question_text': 'What is a firewall?',
                'question_type': 'multiple_choice'
            }
            
            response = client.get('/api/questions/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['question']['id'] == '1'
            assert data['question']['question_text'] == 'What is a firewall?'
            mock_question_manager.get_question.assert_called_once_with('1')
    
    def test_get_question_not_found(self, client, mock_question_manager):
        """Test GET /api/questions/<question_id> when question not found"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question.return_value = None
            
            response = client.get('/api/questions/999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == 'Question not found'
    
    def test_get_question_no_question_manager(self, client):
        """Test GET /api/questions/<question_id> when question_manager is None"""
        with patch('api.question_routes.question_manager', None):
            response = client.get('/api/questions/1')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database not configured' in data['error']
    
    def test_get_question_exception(self, client, mock_question_manager):
        """Test GET /api/questions/<question_id> with exception"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question.side_effect = Exception("Database error")
            
            response = client.get('/api/questions/1')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Database error"
    
    def test_get_categories_success(self, client, mock_question_manager):
        """Test successful GET /api/categories"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_categories.return_value = [
                'Technologies and Tools',
                'Threats, Attacks, and Vulnerabilities',
                'Identity and Access Management',
                'Cryptography and PKI'
            ]
            
            response = client.get('/api/categories')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['categories']) == 4
            assert 'Technologies and Tools' in data['categories']
            mock_question_manager.get_question_categories.assert_called_once()
    
    def test_get_categories_no_question_manager(self, client):
        """Test GET /api/categories when question_manager is None"""
        with patch('api.question_routes.question_manager', None):
            response = client.get('/api/categories')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database not configured' in data['error']
    
    def test_get_categories_exception(self, client, mock_question_manager):
        """Test GET /api/categories with exception"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_categories.side_effect = Exception("Database error")
            
            response = client.get('/api/categories')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Database error"
    
    def test_get_tags_success(self, client, mock_question_manager):
        """Test successful GET /api/tags"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_tags.return_value = [
                'firewall', 'security', 'network', 'encryption', 'authentication'
            ]
            
            response = client.get('/api/tags')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['tags']) == 5
            assert 'firewall' in data['tags']
            assert 'security' in data['tags']
            mock_question_manager.get_question_tags.assert_called_once()
    
    def test_get_tags_no_question_manager(self, client):
        """Test GET /api/tags when question_manager is None"""
        with patch('api.question_routes.question_manager', None):
            response = client.get('/api/tags')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database not configured' in data['error']
    
    def test_get_tags_exception(self, client, mock_question_manager):
        """Test GET /api/tags with exception"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_tags.side_effect = Exception("Database error")
            
            response = client.get('/api/tags')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Database error"
    
    def test_get_stats_success(self, client, mock_question_manager):
        """Test successful GET /api/stats"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_count.return_value = 10
            mock_question_manager.get_question_categories.return_value = [
                'Technologies and Tools',
                'Threats, Attacks, and Vulnerabilities'
            ]
            mock_question_manager.get_question_tags.return_value = [
                'firewall', 'security', 'network'
            ]
            
            # Mock get_question_count for specific categories
            def mock_get_count(category=None):
                if category == 'Technologies and Tools':
                    return 5
                elif category == 'Threats, Attacks, and Vulnerabilities':
                    return 5
                return 10
            
            mock_question_manager.get_question_count.side_effect = mock_get_count
            
            response = client.get('/api/stats')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'stats' in data
            
            stats = data['stats']
            assert stats['total_questions'] == 10
            assert stats['total_categories'] == 2
            assert stats['total_tags'] == 3
            assert 'category_breakdown' in stats
            assert stats['category_breakdown']['Technologies and Tools'] == 5
            assert stats['category_breakdown']['Threats, Attacks, and Vulnerabilities'] == 5
    
    def test_get_stats_no_question_manager(self, client):
        """Test GET /api/stats when question_manager is None"""
        with patch('api.question_routes.question_manager', None):
            response = client.get('/api/stats')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Database not configured' in data['error']
    
    def test_get_stats_exception(self, client, mock_question_manager):
        """Test GET /api/stats with exception"""
        with patch('api.question_routes.question_manager', mock_question_manager):
            mock_question_manager.get_question_count.side_effect = Exception("Database error")
            
            response = client.get('/api/stats')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Database error"
    
    def test_invalid_route(self, client):
        """Test accessing invalid API route"""
        response = client.get('/api/invalid')
        
        assert response.status_code == 404
    
    def test_api_blueprint_registration(self, app):
        """Test that the API blueprint is properly registered"""
        # Check if the blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'question_api' in blueprint_names
        
        # Check if routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/api/questions' in rules
        assert '/api/questions/<question_id>' in rules
        assert '/api/categories' in rules
        assert '/api/tags' in rules
        assert '/api/stats' in rules
