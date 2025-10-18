from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import os
from api.question_routes import question_api

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Register API blueprints
app.register_blueprint(question_api)

# Mock user database (in production, use a real database)
users = {}

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
    
    if not answer:
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
    
    # Otherwise, redirect to next question
    next_question_number = result['question_number']
    return redirect(url_for('quiz_question', quiz_id=quiz_id, question_number=next_question_number))

@app.route('/quiz/<quiz_id>/results')
def quiz_results(quiz_id):
    """Display quiz results"""
    from services.quiz_service import quiz_service
    
    results = quiz_service.get_quiz_results(quiz_id)
    
    if not results:
        flash('Quiz results not found.', 'error')
        return redirect(url_for('quizzes'))
    
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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Mock authentication (in production, verify against database)
        if email in users and users[email]['password'] == password:
            session['user'] = email
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page route"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        experience_level = request.form.get('experience_level')
        interests = request.form.get('interests')
        terms = request.form.get('terms')
        newsletter = request.form.get('newsletter')
        
        # Basic validation
        if not all([first_name, last_name, email, password, confirm_password, experience_level, interests, terms]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if email in users:
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('login'))
        
        # Store user data (in production, hash password and store in database)
        users[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'experience_level': experience_level,
            'interests': interests,
            'newsletter': bool(newsletter)
        }
        
        flash('Registration successful! Please login to continue.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Avoid Flask reloader spawning an extra process which would lose in-memory quiz sessions
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port, use_reloader=False)
