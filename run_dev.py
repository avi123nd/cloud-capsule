#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Development server startup script for Time Capsule Cloud

This script sets up the development environment and starts the Flask server.
"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix UTF-8 encoding on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_environment():
    """Check if all required environment variables are set (MongoDB stack)."""
    required_vars = [
        'MONGO_URI',
        'JWT_SECRET',
        'ENCRYPTION_KEY',
        'SECRET_KEY'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all variables are set.")
        return False

    # Validate encryption key length
    enc = os.getenv('ENCRYPTION_KEY', '')
    if len(enc) != 32:
        print("❌ ENCRYPTION_KEY must be exactly 32 characters long")
        return False

    return True

def main():
    """Main function to start the development server."""
    print("🚀 Starting Time Capsule Cloud Development Server")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    print("✅ MongoDB configuration ready")
    print("✅ Encryption service ready")
    print("✅ JWT authentication ready")
    print("\n🌐 Starting Flask development server...")
    print("📡 API will be available at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the Flask app
    try:
        from app import create_app
        app = create_app()
        # debug=False to disable reloader so print statements show up
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
