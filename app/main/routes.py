from flask import render_template, request, redirect, url_for, flash
from app.main import bp

@bp.route('/')
def index():
    """Home page route"""
    return render_template('main/index.html')

@bp.route('/about')
def about():
    """About page route"""
    return render_template('main/about.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Basic validation
        if not all([name, email, subject, message]):
            flash('Please fill in all required fields.', 'error')
            return render_template('main/contact.html')
        
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('main/contact.html')
        
        # Here you would typically send an email or save to database
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html')

def is_valid_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None
