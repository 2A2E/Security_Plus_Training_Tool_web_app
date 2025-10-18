#!/usr/bin/env python3
"""
Main application entry point for Security Plus Training Tool
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from main.py
from main import app

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    print(f"Starting Security Plus Training Tool on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    # Disable reloader so in-memory sessions remain stable
    app.run(host=host, port=port, debug=debug, use_reloader=False)
