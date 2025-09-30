from flask import Flask
from config import config

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions (for future use)
    # db.init_app(app)
    # login_manager.init_app(app)
    # migrate.init_app(app, db)
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.training import bp as training_bp
    app.register_blueprint(training_bp, url_prefix='/training')
    
    # Error handlers
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    return app
