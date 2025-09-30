from flask import render_template, request, redirect, url_for, flash, session
from app.auth import bp
from app.auth.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Mock authentication (in production, verify against database)
        user = User.get_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['logged_in'] = True
            if remember:
                session.permanent = True
            
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
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
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if User.get_by_email(email):
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('auth.login'))
        
        # Create new user
        user = User.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            experience_level=experience_level,
            interests=interests,
            newsletter=bool(newsletter)
        )
        
        flash('Registration successful! Please login to continue.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
