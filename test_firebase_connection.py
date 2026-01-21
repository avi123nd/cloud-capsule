#!/usr/bin/env python3
"""
Test Firebase connection for Time Capsule Cloud

This script tests the Firebase connection and configuration.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_STORAGE_BUCKET',
        'ENCRYPTION_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {value[:20]}..." if len(value) > 20 else f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"  ❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ All required environment variables are set")
    return True

def test_firebase_import():
    """Test Firebase SDK import."""
    print("\n🔍 Testing Firebase SDK import...")
    
    try:
        import firebase_admin
        print("  ✅ firebase_admin imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Failed to import firebase_admin: {e}")
        return False

def test_firebase_initialization():
    """Test Firebase initialization."""
    print("\n🔍 Testing Firebase initialization...")
    
    try:
        from app import initialize_firebase
        initialize_firebase()
        print("  ✅ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Firebase initialization failed: {e}")
        print("  💡 Make sure you have updated .env with service account credentials")
        return False

def test_app_creation():
    """Test Flask app creation."""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        from app import create_app
        app = create_app()
        print("  ✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Flask app creation failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Time Capsule Cloud - Firebase Connection Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        test_environment_variables,
        test_firebase_import,
        test_firebase_initialization,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Firebase configuration is ready.")
        print("🚀 You can now run: python run_dev.py")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        print("📝 Make sure to:")
        print("   1. Complete Firebase Console setup")
        print("   2. Update .env with service account credentials")
        print("   3. Install all dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
