"""
API routes for question management
"""
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Import question manager with error handling
try:
    from database.question_manager import question_manager
except ImportError:
    logger.error("Could not import question_manager - database not configured")
    question_manager = None

# Create blueprint for question API routes
question_api = Blueprint('question_api', __name__, url_prefix='/api')

@question_api.route('/questions')
def get_questions():
    """API endpoint to get questions with optional filtering"""
    if not question_manager:
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please implement database connection.'
        }), 503
    
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        tags = request.args.getlist('tags')
        limit = int(request.args.get('limit', 10))
        skip = int(request.args.get('skip', 0))
        
        questions = question_manager.get_questions(
            category=category,
            difficulty=difficulty,
            tags=tags if tags else None,
            limit=limit,
            skip=skip
        )
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/questions/<question_id>')
def get_question(question_id):
    """API endpoint to get a specific question by ID"""
    if not question_manager:
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please implement database connection.'
        }), 503
    
    try:
        question = question_manager.get_question(question_id)
        if question:
            return jsonify({
                'success': True,
                'question': question
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/categories')
def get_categories():
    """API endpoint to get all question categories"""
    if not question_manager:
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please implement database connection.'
        }), 503
    
    try:
        categories = question_manager.get_question_categories()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/tags')
def get_tags():
    """API endpoint to get all question tags"""
    if not question_manager:
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please implement database connection.'
        }), 503
    
    try:
        tags = question_manager.get_question_tags()
        return jsonify({
            'success': True,
            'tags': tags
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/stats')
def get_stats():
    """API endpoint to get database statistics"""
    if not question_manager:
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please implement database connection.'
        }), 503
    
    try:
        total_questions = question_manager.get_question_count()
        categories = question_manager.get_question_categories()
        tags = question_manager.get_question_tags()
        
        # Get count by category
        category_stats = {}
        for category in categories:
            count = question_manager.get_question_count(category=category)
            category_stats[category] = count
        
        return jsonify({
            'success': True,
            'stats': {
                'total_questions': total_questions,
                'total_categories': len(categories),
                'total_tags': len(tags),
                'category_breakdown': category_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
