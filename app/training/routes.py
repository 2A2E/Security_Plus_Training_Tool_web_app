from flask import render_template, request, redirect, url_for, flash, session
from app.training import bp

@bp.route('/')
def index():
    """Training page route"""
    return render_template('training/index.html')

@bp.route('/beginner')
def beginner():
    """Beginner training modules"""
    return render_template('training/beginner.html')

@bp.route('/intermediate')
def intermediate():
    """Intermediate training modules"""
    return render_template('training/intermediate.html')

@bp.route('/advanced')
def advanced():
    """Advanced training modules"""
    return render_template('training/advanced.html')

@bp.route('/certification')
def certification():
    """Certification preparation modules"""
    return render_template('training/certification.html')

@bp.route('/module/<module_id>')
def module_detail(module_id):
    """Individual module detail page"""
    # In production, fetch module details from database
    return render_template('training/module_detail.html', module_id=module_id)

@bp.route('/quiz/<module_id>')
def quiz(module_id):
    """Quiz page for a module"""
    # Check if user is logged in
    if not session.get('logged_in'):
        flash('Please login to access quizzes.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('training/quiz.html', module_id=module_id)

@bp.route('/progress')
def progress():
    """User progress tracking page"""
    if not session.get('logged_in'):
        flash('Please login to view your progress.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('training/progress.html')
