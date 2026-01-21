"""
Time Capsule Cloud - Flask Backend Application

This module contains the main Flask application with MongoDB integration,
JWT-based user authentication, capsule management, and scheduling functionality.
"""

import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import jwt
from apscheduler.schedulers.background import BackgroundScheduler

from services.auth_service import AuthService
from services.encryption_service import EncryptionService
from services.capsule_service import CapsuleService
from services.scheduler_service import SchedulerService
from services.email_service import EmailService

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
JWT_SECRET = os.getenv('JWT_SECRET')

# Extract database name from URI or use default
def get_database_name():
    """Extract database name from MONGO_URI or use default."""
    if not MONGO_URI:
        return 'timecapsule'
    
    # If URI contains database name (mongodb://host/dbname)
    if '/' in MONGO_URI.rsplit('?', 1)[0]:
        db_name = MONGO_URI.rsplit('/', 1)[-1].split('?')[0]
        if db_name and db_name != 'mongodb' and ':' not in db_name:
            return db_name
    return 'timecapsule'  # Default database name

client = MongoClient(MONGO_URI)
db = client[get_database_name()]

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

    # Services
    auth_service = AuthService(db, JWT_SECRET)
    encryption_service = EncryptionService()
    capsule_service = CapsuleService(db, encryption_service)
    email_service = EmailService()
    scheduler_service = SchedulerService(db, capsule_service, email_service)
    scheduler_service.start_scheduler()

    # Register endpoints (update routes files to take new services)
    from routes.auth_routes import auth_bp
    from routes.capsule_routes import capsule_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.user_routes import user_bp
    from routes.notification_routes import notifications_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(capsule_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(notifications_bp)

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'time': datetime.utcnow().isoformat()})

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large', 'message': 'Max file size is 100MB'}), 413

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
