#!/usr/bin/env python3
"""
Main application entry point for Security Plus Training Tool
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from app.py (not the app/ directory)
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    print(f"Starting Security Plus Training Tool on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
