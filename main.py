from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import os
import traceback
from api.question_routes import question_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

# Add error handler for debugging
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}", exc_info=True)
    return "Internal Server Error", 500

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Register API blueprints
app.register_blueprint(question_api)

# Import auth service
from services.auth_service import auth_service, login_required

# Context processor to make authentication state available in templates
@app.context_processor
def inject_auth_state():
    """Make authentication state available to all templates"""
    is_authenticated = 'user_id' in session
    user_email = session.get('user_email', '')
    return dict(is_authenticated=is_authenticated, user_email=user_email)

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page route"""
    return render_template('contact.html')

@app.route('/training')
def training():
    """Training page route"""
    return render_template('training.html')

@app.route('/flashcards')
def flashcards():
    """Flashcards page route"""
    return render_template('flashcards.html')

@app.route('/flashcards/section/<int:section>')
def flashcard_section(section):
    """Flashcard viewer page for specific section"""
    from services.flashcard_service import flashcard_service
    
    # Create flashcard session (no limit: include all cards for pagination)
    session_id = flashcard_service.create_flashcard_session(section, limit=None)
    
    if not session_id:
        flash('No questions found for this section. Please add questions to the database.', 'error')
        return redirect(url_for('flashcards'))
    
    # Track flashcard progress if user is logged in
    user_id = session.get('user_id')
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    if user_id:
        from services.progress_service import progress_service
        # Get flashcard count for this session
        flashcard = flashcard_service.get_flashcard(session_id, 1)
        if flashcard:
            total_cards = flashcard.get('total_cards', 1)
            # Save progress (we'll track views per card, but for now track session)
            try:
                save_result = progress_service.save_flashcard_progress(
                    user_id=user_id,
                    section=section,
                    cards_viewed=1,  # Track initial view, could be enhanced to track per card
                    session_id=session_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                if not save_result.get('success'):
                    logger.warning(f"Failed to save flashcard progress: {save_result.get('error')}")
            except Exception as e:
                logger.error(f"Error saving flashcard progress: {e}", exc_info=True)
    
    # Get the first flashcard
    current_flashcard = flashcard_service.get_flashcard(session_id, 1)
    
    if not current_flashcard:
        flash('Error loading flashcard questions.', 'error')
        return redirect(url_for('flashcards'))
    
    # Get section info for title
    section_info = flashcard_service.get_section_info(section)
    section_title = f"Section {section}: {section_info['name']}" if section_info else f"Section {section}"
    
    return render_template('flashcard_viewer.html',
                         section_title=section_title,
                         current_flashcard=current_flashcard,
                         current_card_number=current_flashcard['card_number'],
                         total_cards=current_flashcard['total_cards'],
                         session_id=session_id)

@app.route('/quizzes')
def quizzes():
    """Quizzes page route"""
    return render_template('quizzes.html')

@app.route('/practice-test')
def practice_test():
    """Practice test page route"""
    return render_template('practice_test.html')

@app.route('/quiz/section/<int:section>')
def quiz_section(section):
    """Quiz page for specific section"""
    from services.quiz_service import quiz_service
    
    # Create quiz session
    quiz_id = quiz_service.create_section_quiz(section, limit=10)
    
    if not quiz_id:
        flash('No questions found for this section. Please add questions to the database.', 'error')
        return redirect(url_for('quizzes'))
    
    # Get the first question
    current_question = quiz_service.get_quiz_question(quiz_id, 1)
    
    if not current_question:
        flash('Error loading quiz questions.', 'error')
        return redirect(url_for('quizzes'))
    
    # Get section info for title
    section_info = quiz_service.get_section_info(section)
    quiz_title = f"Section {section}: {section_info['name']}" if section_info else f"Section {section}"
    
    return render_template('quiz.html',
                         quiz_title=quiz_title,
                         quiz_type='Section Quiz',
                         current_question=current_question,
                         current_question_number=current_question['question_number'],
                         total_questions=current_question['total_questions'],
                         progress_percentage=current_question['progress_percentage'],
                         show_explanation=False,
                         quiz_id=quiz_id)

@app.route('/quiz/chapter/<int:chapter>')
def quiz_chapter(chapter):
    """Quiz page for specific chapter (legacy support)"""
    # Redirect to section-based quiz
    return redirect(url_for('quiz_section', section=chapter))

@app.route('/quiz/random')
def quiz_random():
    """Random quiz page"""
    from services.quiz_service import quiz_service
    
    # Create random quiz session
    quiz_id = quiz_service.create_random_quiz(limit=10)
    
    if not quiz_id:
        flash('No questions found. Please add questions to the database.', 'error')
        return redirect(url_for('quizzes'))
    
    # Get the first question
    current_question = quiz_service.get_quiz_question(quiz_id, 1)
    
    if not current_question:
        flash('Error loading quiz questions.', 'error')
        return redirect(url_for('quizzes'))
    
    return render_template('quiz.html',
                         quiz_title='Random Quiz',
                         quiz_type='Random Quiz',
                         current_question=current_question,
                         current_question_number=current_question['question_number'],
                         total_questions=current_question['total_questions'],
                         progress_percentage=current_question['progress_percentage'],
                         show_explanation=False,
                         quiz_id=quiz_id)

@app.route('/quiz/practice-test')
def quiz_practice_test():
    """Full practice test page (90 questions)"""
    from services.quiz_service import quiz_service
    
    # Create practice test session
    quiz_id = quiz_service.create_full_practice_test()
    
    if not quiz_id:
        flash('Not enough questions found for practice test. Please add more questions to the database.', 'error')
        return redirect(url_for('quizzes'))
    
    # Get the first question
    current_question = quiz_service.get_quiz_question(quiz_id, 1)
    
    if not current_question:
        flash('Error loading practice test questions.', 'error')
        return redirect(url_for('quizzes'))
    
    return render_template('quiz.html',
                         quiz_title='Practice Test (90 Questions)',
                         quiz_type='Practice Test',
                         current_question=current_question,
                         current_question_number=current_question['question_number'],
                         total_questions=current_question['total_questions'],
                         progress_percentage=current_question['progress_percentage'],
                         show_explanation=False,
                         quiz_id=quiz_id)

@app.route('/quiz/<quiz_id>/question/<int:question_number>')
def quiz_question(quiz_id, question_number):
    """Get a specific question from a quiz"""
    from services.quiz_service import quiz_service
    
    current_question = quiz_service.get_quiz_question(quiz_id, question_number)
    
    if not current_question:
        flash('Question not found.', 'error')
        return redirect(url_for('quizzes'))
    
    # Detect quiz type from quiz_id
    if quiz_id.startswith('practice_test'):
        quiz_title = f'Practice Test - Question {question_number} of {current_question["total_questions"]}'
        quiz_type = 'Practice Test'
    elif quiz_id.startswith('section_quiz'):
        quiz_title = f'Section Quiz - Question {question_number}'
        quiz_type = 'Section Quiz'
    elif quiz_id.startswith('random_quiz'):
        quiz_title = f'Random Quiz - Question {question_number}'
        quiz_type = 'Random Quiz'
    else:
        quiz_title = f'Quiz Question {question_number}'
        quiz_type = 'Quiz'
    
    return render_template('quiz.html',
                         quiz_title=quiz_title,
                         quiz_type=quiz_type,
                         current_question=current_question,
                         current_question_number=current_question['question_number'],
                         total_questions=current_question['total_questions'],
                         progress_percentage=current_question['progress_percentage'],
                         show_explanation=False,
                         quiz_id=quiz_id)

@app.route('/quiz/<quiz_id>/submit', methods=['POST'])
def submit_quiz_answer(quiz_id):
    """Submit an answer for the current question"""
    from services.quiz_service import quiz_service
    
    # Debug logging for troubleshooting submit issues
    try:
        logging.getLogger(__name__).info(f"[submit] quiz_id={quiz_id} form_keys={list(request.form.keys())}")
    except Exception:
        pass
    answer = request.form.get('answer', '').strip()
    
    if not answer or answer == 'skip':
        if answer == 'skip':
            # Handle skip - move to next question without showing result
            result = quiz_service.submit_quiz_answer(quiz_id, answer)
            if result and result.get('quiz_completed'):
                return redirect(url_for('quiz_results', quiz_id=quiz_id))
            elif result:
                next_question_number = result['question_number']
                return redirect(url_for('quiz_question', quiz_id=quiz_id, question_number=next_question_number))
        flash('Please select an answer.', 'error')
        return redirect(request.referrer or url_for('quizzes'))
    
    result = quiz_service.submit_quiz_answer(quiz_id, answer)
    
    if not result:
        # Provide more detail if available
        flash('Error submitting answer.', 'error')
        return redirect(url_for('quizzes'))
    
    # If quiz is completed, redirect to results
    if result.get('quiz_completed'):
        return redirect(url_for('quiz_results', quiz_id=quiz_id))
    
    # Get the question that was just answered (before it advanced)
    # We need to get it from the session's questions list using the index
    from utils.quiz_logic import quiz_manager
    session = quiz_manager.get_session(quiz_id)
    if not session:
        flash('Error loading question.', 'error')
        return redirect(url_for('quizzes'))
    
    # The question_index in the answer_data is the index before submission
    # Get the last answer to find which question was answered
    if session.answers:
        last_answer = session.answers[-1]
        answered_index = last_answer.get('question_index', 0)
        if answered_index < len(session.questions):
            current_question = session.questions[answered_index].copy()
            current_question_number = answered_index + 1
        else:
            flash('Error loading question.', 'error')
            return redirect(url_for('quizzes'))
    else:
        flash('Error loading question.', 'error')
        return redirect(url_for('quizzes'))
    
    # Add quiz metadata
    current_question['quiz_id'] = quiz_id
    current_question['question_number'] = current_question_number
    current_question['total_questions'] = session.total_questions
    current_question['progress_percentage'] = (current_question_number / session.total_questions) * 100
    
    # Get section info for title
    section_info = quiz_service.get_section_info(current_question.get('section', 1))
    quiz_title = f"Section {current_question.get('section', 1)}: {section_info['name']}" if section_info else f"Section {current_question.get('section', 1)}"
    
    # Detect quiz type from quiz_id
    if quiz_id.startswith('practice_test'):
        quiz_title = f'Practice Test - Question {current_question_number} of {current_question["total_questions"]}'
        quiz_type = 'Practice Test'
    elif quiz_id.startswith('section_quiz'):
        quiz_title = f'Section Quiz - Question {current_question_number}'
        quiz_type = 'Section Quiz'
    elif quiz_id.startswith('random_quiz'):
        quiz_title = f'Random Quiz - Question {current_question_number}'
        quiz_type = 'Random Quiz'
    else:
        quiz_title = f'Quiz Question {current_question_number}'
        quiz_type = 'Quiz'
    
    # Get correct answer index for multiple choice questions
    correct_answer_index = None
    if current_question.get('question_type') in ['multiple_choice', 'concept_multiple_choice', 'scenario_multiple_choice']:
        correct_answer = current_question.get('correct_answer', '')
        if isinstance(correct_answer, (int, str)) and str(correct_answer).isdigit():
            correct_answer_index = int(correct_answer)
        else:
            # Find index of correct answer text in options
            options = current_question.get('options', [])
            for idx, option in enumerate(options):
                if str(option).strip().lower() == str(correct_answer).strip().lower():
                    correct_answer_index = idx
                    break
    
    return render_template('quiz.html',
                         quiz_title=quiz_title,
                         quiz_type=quiz_type,
                         current_question=current_question,
                         current_question_number=current_question_number,
                         total_questions=current_question['total_questions'],
                         progress_percentage=current_question['progress_percentage'],
                         show_explanation=True,
                         is_correct=result.get('is_correct', False),
                         user_answer=result.get('user_answer', ''),
                         correct_answer=result.get('correct_answer', ''),
                         correct_answer_index=correct_answer_index,
                         explanation=result.get('explanation', ''),
                         quiz_id=quiz_id)

@app.route('/quiz/<quiz_id>/results')
def quiz_results(quiz_id):
    """Display quiz results"""
    from services.quiz_service import quiz_service
    
    results = quiz_service.get_quiz_results(quiz_id)
    
    if not results:
        flash('Quiz results not found.', 'error')
        return redirect(url_for('quizzes'))
    
    # Save quiz result to database if user is logged in
    user_id = session.get('user_id')
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    if user_id:
        from services.progress_service import progress_service
        
        # Extract section from quiz_id if it's a section quiz
        section = None
        if quiz_id.startswith('section_quiz_'):
            try:
                # Extract section from quiz_id format: section_quiz_{section}_{timestamp}
                parts = quiz_id.split('_')
                if len(parts) >= 3:
                    section = int(parts[2])
            except (ValueError, IndexError):
                pass
        
        # Prepare quiz result data
        quiz_result_data = {
            'quiz_id': quiz_id,
            'quiz_type': results.get('quiz_type', 'unknown'),
            'section': section,
            'score': results.get('score', 0),
            'total_questions': results.get('total_questions', 0),
            'percentage': results.get('percentage', 0),
            'duration_seconds': int(results.get('duration_seconds', 0))
        }
        
        # Save to database
        try:
            save_result = progress_service.save_quiz_result(user_id, quiz_result_data, access_token=access_token, refresh_token=refresh_token)
            if not save_result.get('success'):
                logger.warning(f"Failed to save quiz result: {save_result.get('error')}")
            else:
                logger.info(f"Successfully saved quiz result for user {user_id[:8]}...")
        except Exception as e:
            logger.error(f"Error saving quiz result: {e}", exc_info=True)
        
        # Save study session
        if results.get('duration_seconds'):
            try:
                progress_service.save_study_session(
                    user_id=user_id,
                    session_type=results.get('quiz_type', 'quiz'),
                    duration_seconds=int(results.get('duration_seconds', 0)),
                    section=section,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
            except Exception as e:
                logger.error(f"Error saving study session: {e}", exc_info=True)
    
    # Get wrong questions for review
    wrong_questions = quiz_service.get_wrong_questions_review(quiz_id)
    
    # Format results for template
    formatted_results = {
        'quiz_type': results.get('quiz_type', 'Quiz'),
        'chapter': results.get('chapter'),
        'score': results.get('score', 0),
        'total_questions': results.get('total_questions', 0),
        'percentage': results.get('percentage', 0),
        'wrong_questions': results.get('wrong_questions', 0),
        'duration_seconds': results.get('duration_seconds', 0)
    }
    
    return render_template('quiz_results.html',
                         results=formatted_results,
                         wrong_questions=wrong_questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')
        
        # Authenticate with Supabase Auth
        result = auth_service.login_user(email, password)
        
        if result['success']:
            # Store session data
            session['user_id'] = result['user'].id
            session['user_email'] = result['user'].email
            session['access_token'] = result['session'].access_token
            session['refresh_token'] = result['session'].refresh_token
            session['logged_in'] = True
            
            # Set session permanent if remember me is checked
            if remember:
                session.permanent = True
            
            flash(result['message'], 'success')
            return redirect(url_for('home'))
        else:
            flash(result['error'], 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page route"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        experience_level = request.form.get('experience_level')
        
        # Basic validation
        if not all([first_name, last_name, email, password, confirm_password, experience_level]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        # Prepare user metadata
        user_metadata = {
            'first_name': first_name,
            'last_name': last_name,
            'experience_level': experience_level
        }
        
        # Register with Supabase Auth
        result = auth_service.register_user(email, password, user_metadata, auto_confirm=True)
        
        if result['success']:
            # If we got a session back, auto-login the user
            if result.get('session'):
                session['user_id'] = result['user'].id
                session['user_email'] = result['user'].email
                session['access_token'] = result['session'].access_token
                session['refresh_token'] = result['session'].refresh_token
                session['logged_in'] = True
                
                flash('Registration successful! Welcome to Security+ Exam Prep.', 'success')
                return redirect(url_for('home'))
            else:
                # No session means email confirmation is required
                flash('Registration successful! Thank you for registering. You can now login with your email and password.', 'success')
                return redirect(url_for('login'))
        else:
            flash(result['error'], 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout route"""
    # Sign out from Supabase if access token exists
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    
    if access_token and refresh_token:
        auth_service.logout_user(access_token=access_token, refresh_token=refresh_token)
    
    # Clear session
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/auth/callback')
def auth_callback():
    """
    Handle Supabase auth callback (email confirmation, password reset, etc.)
    This route handles the redirect from Supabase after email confirmation
    """
    # Get tokens from URL parameters (Supabase redirects here)
    access_token = request.args.get('access_token')
    refresh_token = request.args.get('refresh_token')
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    # Log for debugging
    logger.info(f"Auth callback - access_token: {'present' if access_token else 'missing'}, refresh_token: {'present' if refresh_token else 'missing'}, error: {error}")
    
    # If no tokens in query params, render the JavaScript handler page
    # This handles cases where Supabase sends tokens in URL hash (#)
    if not access_token and not refresh_token and not error:
        return render_template('auth_callback.html')
    
    # Handle errors
    if error:
        error_msg = error_description or error
        flash(f'Authentication error: {error_msg}', 'error')
        return redirect(url_for('login'))
    
    # If we have tokens, set up the session
    if access_token and refresh_token:
        try:
            # Get user info using the tokens
            user_profile = auth_service.get_user_profile(access_token=access_token, refresh_token=refresh_token)
            
            if user_profile:
                # Store session data
                session['user_id'] = user_profile['id']
                session['user_email'] = user_profile['email']
                session['access_token'] = access_token
                session['refresh_token'] = refresh_token
                session['logged_in'] = True
                
                flash('Email confirmed successfully! You are now logged in.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Could not verify your account. Please try logging in.', 'error')
                return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error handling auth callback: {e}")
            flash('Error confirming your email. Please try logging in.', 'error')
            return redirect(url_for('login'))
    
    # If no tokens, redirect to login
    flash('Invalid confirmation link. Please try logging in.', 'error')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page route"""
    try:
        # Get user profile data
        access_token = session.get('access_token')
        refresh_token = session.get('refresh_token')
        user_id = session.get('user_id')
        
        # Handle profile update
        if request.method == 'POST':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            experience_level = request.form.get('experience_level', '').strip()
            
            if not first_name or not last_name or not experience_level:
                flash('Please fill in all required fields.', 'error')
            else:
                # Prepare metadata update
                metadata = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'experience_level': experience_level
                }
                
                # Update user metadata
                try:
                    result = auth_service.update_user_metadata(access_token=access_token, refresh_token=refresh_token, metadata=metadata)
                    
                    if result.get('success'):
                        flash('Profile updated successfully!', 'success')
                    else:
                        flash(result.get('error', 'Failed to update profile.'), 'error')
                except Exception as e:
                    logger.error(f"Error updating user metadata: {e}")
                    flash('Failed to update profile. Please try again.', 'error')
            
            # Redirect to profile page to show updated data
            return redirect(url_for('profile'))
        
        # Get user profile data
        try:
            user_profile = auth_service.get_user_profile(access_token=access_token, refresh_token=refresh_token)
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            flash('Unable to load profile. Please try logging in again.', 'error')
            session.clear()
            return redirect(url_for('login'))
        
        if not user_profile:
            flash('Unable to load profile. Please try logging in again.', 'error')
            session.clear()
            return redirect(url_for('login'))
        
        # Get user statistics from progress service
        try:
            from services.progress_service import progress_service
            if user_id:
                statistics = progress_service.get_user_statistics(
                    user_id,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
            else:
                statistics = {
                    'total_quizzes': 0,
                    'total_flashcards': 0,
                    'total_practice_tests': 0,
                    'average_score': 0,
                    'total_study_time_hours': 0
                }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}", exc_info=True)
            # Provide default statistics if there's an error
            statistics = {
                'total_quizzes': 0,
                'total_flashcards': 0,
                'total_practice_tests': 0,
                'average_score': 0,
                'total_study_time_hours': 0
            }
        
        # Ensure statistics is always a dict with all required keys
        if not isinstance(statistics, dict):
            statistics = {
                'total_quizzes': 0,
                'total_flashcards': 0,
                'total_practice_tests': 0,
                'average_score': 0,
                'total_study_time_hours': 0
            }
        
        # Ensure all required keys exist in statistics
        required_stat_keys = ['total_quizzes', 'total_flashcards', 'total_practice_tests', 'average_score', 'total_study_time_hours']
        for key in required_stat_keys:
            if key not in statistics:
                statistics[key] = 0
        
        return render_template('profile.html', user_profile=user_profile, statistics=statistics)
    
    except Exception as e:
        logger.error(f"Error in profile route: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback:\n{error_details}")
        flash(f'An error occurred while loading your profile: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page route"""
    # Get user profile data
    access_token = session.get('access_token')
    refresh_token = session.get('refresh_token')
    user_id = session.get('user_id')
    
    user_profile = auth_service.get_user_profile(access_token=access_token, refresh_token=refresh_token)
    
    if not user_profile:
        flash('Unable to load dashboard. Please try logging in again.', 'error')
        session.clear()
        return redirect(url_for('login'))
    
    # Get dashboard data from progress service
    from services.progress_service import progress_service
    
    # Get statistics
    statistics = progress_service.get_user_statistics(
        user_id,
        access_token=access_token,
        refresh_token=refresh_token
    ) if user_id else {
        'total_quizzes': 0,
        'total_flashcards': 0,
        'total_practice_tests': 0,
        'average_score': 0,
        'total_study_time_hours': 0
    }
    
    # Get recent quiz history
    recent_quizzes = progress_service.get_user_quiz_history(
        user_id,
        limit=10,
        access_token=access_token,
        refresh_token=refresh_token
    ) if user_id else []
    
    # Get section progress
    section_progress = progress_service.get_section_progress(
        user_id,
        access_token=access_token,
        refresh_token=refresh_token
    ) if user_id else {}
    
    # Get study time
    study_time = progress_service.get_study_time(
        user_id,
        days=30,
        access_token=access_token,
        refresh_token=refresh_token
    ) if user_id else {
        'total_hours': 0,
        'daily_average_hours': 0,
        'sessions_count': 0
    }
    
    # Get performance trends
    performance_trends = progress_service.get_performance_trends(
        user_id,
        days=30,
        access_token=access_token,
        refresh_token=refresh_token
    ) if user_id else []
    
    # Section names for display
    section_names = {
        1: 'General Security Concepts',
        2: 'Threats, Vulnerabilities, and Mitigations',
        3: 'Security Architecture',
        4: 'Security Operations',
        5: 'Security Program Management and Oversight'
    }
    
    return render_template('dashboard.html',
                         user_profile=user_profile,
                         statistics=statistics,
                         recent_quizzes=recent_quizzes,
                         section_progress=section_progress,
                         section_names=section_names,
                         study_time=study_time,
                         performance_trends=performance_trends)


if __name__ == '__main__':
    # Avoid Flask reloader spawning an extra process which would lose in-memory quiz sessions
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port, use_reloader=False)
