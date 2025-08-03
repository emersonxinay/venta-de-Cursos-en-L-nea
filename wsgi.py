#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
load_dotenv(os.path.join(project_home, '.env'))

# Import the Flask application
from app import app

# Configure for production
if __name__ != "__main__":
    # Set up logging for production
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CompilandoCode startup')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)