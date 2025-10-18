"""
API routes for question management
"""
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Import question manager and quiz service with error handling
try:
    from database.question_manager import question_manager
    from services.quiz_service import quiz_service
    from services.flashcard_service import flashcard_service
except ImportError:
    logger.error("Could not import question_manager, quiz_service, or flashcard_service - database not configured")
    question_manager = None
    quiz_service = None
    flashcard_service = None

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

# ============================================================================
# NEW SECTION-BASED QUIZ API ENDPOINTS
# ============================================================================

@question_api.route('/quiz/sections')
def get_quiz_sections():
    """API endpoint to get all quiz sections"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        sections = quiz_service.get_all_sections()
        return jsonify({
            'success': True,
            'sections': sections
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/sections/<int:section>')
def get_quiz_section_info(section):
    """API endpoint to get detailed information about a specific section"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        section_info = quiz_service.get_section_info(section)
        if section_info:
            return jsonify({
                'success': True,
                'section': section_info
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Section {section} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/create/section/<int:section>', methods=['POST'])
def create_section_quiz(section):
    """API endpoint to create a quiz for a specific section"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 10)
        difficulty = data.get('difficulty')
        # Normalize difficulty: treat 'mixed'/'all'/empty as no filter
        if isinstance(difficulty, str) and difficulty.strip().lower() in ['mixed', 'all', 'any', '']:
            difficulty = None
        
        quiz_id = quiz_service.create_section_quiz(section=section, limit=limit, difficulty=difficulty)
        
        if quiz_id:
            return jsonify({
                'success': True,
                'quiz_id': quiz_id,
                'section': section,
                'limit': limit,
                'difficulty': difficulty
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to create quiz for section {section}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/create/category', methods=['POST'])
def create_category_quiz():
    """API endpoint to create a quiz for a specific category"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        category = data.get('category')
        limit = data.get('limit', 10)
        difficulty = data.get('difficulty')
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category is required'
            }), 400
        
        quiz_id = quiz_service.create_category_quiz(category=category, limit=limit, difficulty=difficulty)
        
        if quiz_id:
            return jsonify({
                'success': True,
                'quiz_id': quiz_id,
                'category': category,
                'limit': limit,
                'difficulty': difficulty
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to create quiz for category {category}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/create/random', methods=['POST'])
def create_random_quiz():
    """API endpoint to create a random quiz"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 10)
        difficulty = data.get('difficulty')
        
        quiz_id = quiz_service.create_random_quiz(limit=limit, difficulty=difficulty)
        
        if quiz_id:
            return jsonify({
                'success': True,
                'quiz_id': quiz_id,
                'limit': limit,
                'difficulty': difficulty
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create random quiz'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/create/practice-test', methods=['POST'])
def create_practice_test():
    """API endpoint to create a full practice test (90 questions)"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    # Additional guard for missing database connection
    if not getattr(quiz_service, 'question_manager', None):
        logger.error('[practice-test] question_manager is not configured')
        return jsonify({
            'success': False,
            'error': 'Database not configured. Please add your Supabase credentials and seed questions.'
        }), 503
    
    try:
        data = request.get_json() or {}
        logger.info(f"[practice-test] payload={data}")
        difficulty = data.get('difficulty')
        
        # Normalize difficulty: treat 'mixed'/'all'/empty as no filter
        if isinstance(difficulty, str):
            difficulty_lower = difficulty.strip().lower()
            if difficulty_lower in ['mixed', 'all', 'any', '', 'realistic']:
                difficulty = None
            # Note: Don't filter by difficulty for now - causes too few questions
            # Future: only filter if sufficient questions exist
            else:
                difficulty = None  # Temporary: ignore difficulty to avoid empty results
        else:
            difficulty = None
        
        # Optional overrides
        question_count = int(data.get('question_count', 90))
        sections = data.get('sections')
        if isinstance(sections, list):
            try:
                sections = [int(s) for s in sections]
            except (ValueError, TypeError):
                sections = None

        quiz_id = quiz_service.create_practice_test(
            question_count=question_count,
            sections=sections,
            difficulty=difficulty
        )
        
        if quiz_id:
            return jsonify({
                'success': True,
                'quiz_id': quiz_id,
                'difficulty': difficulty,
                'total_questions': question_count
            })
        else:
            logger.error('[practice-test] quiz_service returned None (likely no questions found)')
            return jsonify({
                'success': False,
                'error': 'Failed to create practice test'
            }), 400
    except Exception as e:
        logger.exception('[practice-test] Unhandled exception creating practice test')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/<quiz_id>/question/<int:question_number>')
def get_quiz_question_api(quiz_id, question_number):
    """API endpoint to get a specific question from a quiz"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        question = quiz_service.get_quiz_question(quiz_id, question_number)
        
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

@question_api.route('/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz_answer_api(quiz_id):
    """API endpoint to submit an answer for the current question"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        answer = data.get('answer', '').strip()
        
        if not answer:
            return jsonify({
                'success': False,
                'error': 'Answer is required'
            }), 400
        
        result = quiz_service.submit_quiz_answer(quiz_id, answer)
        
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to submit answer'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/<quiz_id>/results')
def get_quiz_results_api(quiz_id):
    """API endpoint to get quiz results"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        results = quiz_service.get_quiz_results(quiz_id)
        
        if results:
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Quiz results not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/<quiz_id>/review')
def get_quiz_review_api(quiz_id):
    """API endpoint to get wrong questions for review"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        wrong_questions = quiz_service.get_wrong_questions_review(quiz_id)
        
        return jsonify({
            'success': True,
            'wrong_questions': wrong_questions,
            'count': len(wrong_questions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/quiz/statistics')
def get_quiz_statistics():
    """API endpoint to get overall quiz statistics"""
    if not quiz_service:
        return jsonify({
            'success': False,
            'error': 'Quiz service not configured. Please implement database connection.'
        }), 503
    
    try:
        stats = quiz_service.get_quiz_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# FLASHCARD API ENDPOINTS
# ============================================================================

@question_api.route('/flashcards/sections')
def get_flashcard_sections():
    """API endpoint to get all flashcard sections"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        sections = flashcard_service.get_all_sections()
        return jsonify({
            'success': True,
            'sections': sections
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/flashcards/create/section/<int:section>', methods=['POST'])
def create_flashcard_session(section):
    """API endpoint to create a flashcard session for a specific section"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        # Allow passing "all" or null to include all cards in session
        raw_limit = data.get('limit', 50)
        try:
            limit = int(raw_limit) if raw_limit is not None and str(raw_limit).lower() != 'all' else None
        except (TypeError, ValueError):
            limit = None
        
        session_id = flashcard_service.create_flashcard_session(section=section, limit=limit)
        
        if session_id:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'section': section,
                'limit': limit if limit is not None else 'all'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to create flashcard session for section {section}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/flashcards/<session_id>/card/<int:card_number>')
def get_flashcard(session_id, card_number):
    """API endpoint to get a specific flashcard from a session"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        flashcard = flashcard_service.get_flashcard(session_id, card_number)
        
        if flashcard:
            return jsonify({
                'success': True,
                'flashcard': flashcard
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Flashcard not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/flashcards/<session_id>/all')
def get_all_flashcards(session_id):
    """API endpoint to get paginated flashcards from a session for scroll mode"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        # Get pagination parameters from query string
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:  # Limit max per page
            per_page = 50
        
        result = flashcard_service.get_all_flashcards(session_id, page, per_page)
        
        return jsonify({
            'success': True,
            'flashcards': result['flashcards'],
            'pagination': {
                'current_page': result['current_page'],
                'total_pages': result['total_pages'],
                'total_cards': result['total_cards'],
                'per_page': result['per_page'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/flashcards/<session_id>/navigate', methods=['POST'])
def navigate_flashcard(session_id):
    """API endpoint to navigate to next/previous flashcard"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        direction = data.get('direction', '').lower()
        
        if direction not in ['next', 'previous']:
            return jsonify({
                'success': False,
                'error': 'Direction must be "next" or "previous"'
            }), 400
        
        flashcard = flashcard_service.navigate_card(session_id, direction)
        
        if flashcard:
            return jsonify({
                'success': True,
                'flashcard': flashcard
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Cannot navigate in that direction'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@question_api.route('/flashcards/<session_id>/set-card', methods=['POST'])
def set_flashcard(session_id):
    """API endpoint to set current card by number"""
    if not flashcard_service:
        return jsonify({
            'success': False,
            'error': 'Flashcard service not configured. Please implement database connection.'
        }), 503
    
    try:
        data = request.get_json() or {}
        card_number = data.get('card_number')
        
        if not card_number or not isinstance(card_number, int):
            return jsonify({
                'success': False,
                'error': 'card_number is required and must be an integer'
            }), 400
        
        flashcard = flashcard_service.set_current_card(session_id, card_number)
        
        if flashcard:
            return jsonify({
                'success': True,
                'flashcard': flashcard
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid card number'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
