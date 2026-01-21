#!/usr/bin/env python3
"""
Test runner script for Time Capsule Cloud

This script runs the test suite with proper environment setup.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def setup_test_environment():
    """Set up environment variables for testing."""
    # Load environment variables
    load_dotenv()
    
    # Set test-specific environment variables
    os.environ['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY', 'test-key-32-characters-long-123')
    os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test-secret-key')
    os.environ['FLASK_ENV'] = 'testing'

def run_tests():
    """Run the test suite."""
    print("🧪 Running Time Capsule Cloud Test Suite")
    print("=" * 50)
    
    # Setup test environment
    setup_test_environment()
    
    # Run pytest with verbose output
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--color=yes'
        ], check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it: pip install pytest")
        return False

def main():
    """Main function to run tests."""
    success = run_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
