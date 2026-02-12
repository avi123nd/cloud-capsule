"""
Time Capsule Cloud - Flask Backend Application

This module contains the main Flask application with MongoDB integration,
JWT-based user authentication, capsule management, and scheduling functionality.
"""

import os
import traceback
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import jwt
import os
from apscheduler.schedulers.background import BackgroundScheduler

from services.auth_service import AuthService
from services.encryption_service import EncryptionService
from services.capsule_service import CapsuleService
from services.scheduler_service import SchedulerService
from services.email_service import EmailService

# Load .env from project directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)
print(f"📁 Loading .env from: {env_path}")
print(f"🔍 CLOUDINARY_CLOUD_NAME: {os.getenv('CLOUDINARY_CLOUD_NAME')}")

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
    # Pass Flask app to scheduler for proper context handling
    scheduler_service = SchedulerService(db, capsule_service, email_service, app=app)
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
    
    @app.route('/test-email')
    def test_email():
        """Test endpoint to check if email service is working."""
        try:
            test_email_addr = os.getenv('EMAIL_FROM')
            email_service.send_capsule_created_notification(
                recipient_email=test_email_addr,
                recipient_name='Test User',
                sender_name='Test Sender',
                unlock_date=datetime.utcnow()
            )
            return jsonify({'message': f'Test email sent to {test_email_addr}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/debug/services')
    def debug_services():
        """
        Debug endpoint to check all services are working.
        """
        try:
            from services.capsule_service import CapsuleService
            from services.encryption_service import EncryptionService
            from services.cloudinary_service import CloudinaryStorageService
            
            results = {}
            
            # Test encryption service
            try:
                enc_svc = EncryptionService()
                results['encryption'] = {'status': 'ok', 'key_length': len(enc_svc.key)}
            except Exception as e:
                results['encryption'] = {'status': 'error', 'message': str(e)}
            
            # Test capsule service
            try:
                cap_svc = CapsuleService(db, enc_svc if 'enc_svc' in dir() else EncryptionService())
                results['capsule'] = {
                    'status': 'ok',
                    'cloudinary_available': cap_svc.cloudinary_storage is not None,
                    'gridfs_available': hasattr(cap_svc, 'fs')
                }
            except Exception as e:
                results['capsule'] = {'status': 'error', 'message': str(e)}
            
            # Test MongoDB connection
            try:
                db.command('ping')
                results['mongodb'] = {'status': 'ok', 'database': get_database_name()}
            except Exception as e:
                results['mongodb'] = {'status': 'error', 'message': str(e)}
            
            return jsonify(results)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large', 'message': 'Max file size is 100MB'}), 413

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        error_msg = str(e)
        # Get the original error if available
        if hasattr(e, 'original_exception'):
            error_msg = str(e.original_exception)
        return jsonify({
            'error': 'Internal server error',
            'message': error_msg,
            'traceback': traceback.format_exc()
        }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
