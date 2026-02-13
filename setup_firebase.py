#!/usr/bin/env python3
"""
Firebase setup script for Time Capsule Cloud

This script helps configure Firebase for the Time Capsule Cloud project.
"""

import os
import json
from pathlib import Path

def create_env_file():
    """Create .env file with Firebase configuration."""
    env_content = """# Firebase Configuration
FIREBASE_PROJECT_ID=chronolock-b9823
FIREBASE_API_KEY=AIzaSyBMkN_K1ezo10I8s7cPPafMc9zELXcmMjY
FIREBASE_AUTH_DOMAIN=chronolock-b9823.firebaseapp.com
FIREBASE_STORAGE_BUCKET=chronolock-b9823.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=1074174392161
FIREBASE_APP_ID=1:1074174392161:web:41b66a5a89489f16043720
FIREBASE_MEASUREMENT_ID=G-LH4F3C5Q06

# Firebase Admin SDK (Service Account) - You need to download this from Firebase Console
# Go to Project Settings > Service Accounts > Generate New Private Key
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nyour-private-key\\n-----END PRIVATE KEY-----\\n"
FIREBASE_CLIENT_EMAIL=your-service-account@chronolock-b9823.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40chronolock-b9823.iam.gserviceaccount.com

# Prefer using a service account JSON file for backend auth
# Place your downloaded JSON in the project root and set this path
GOOGLE_APPLICATION_CREDENTIALS=service-account.json

# Encryption Configuration
ENCRYPTION_KEY=your-32-byte-encryption-key-here-must-be-32-chars

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Storage Configuration (Admin SDK expects appspot.com)
STORAGE_BUCKET=chronolock-b9823.appspot.com
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with Firebase configuration")

def generate_encryption_key():
    """Generate a secure encryption key."""
    import secrets
    key = secrets.token_urlsafe(32)[:32]
    return key

def generate_secret_key():
    """Generate a secure Flask secret key."""
    import secrets
    return secrets.token_urlsafe(32)

def update_env_with_keys():
    """Update .env file with generated keys."""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Run create_env_file() first.")
        return
    
    # Generate keys
    encryption_key = generate_encryption_key()
    secret_key = generate_secret_key()
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Replace placeholder keys
    content = content.replace('your-32-byte-encryption-key-here-must-be-32-chars', encryption_key)
    content = content.replace('your-secret-key-here', secret_key)
    
    # Write updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Updated .env file with generated encryption and secret keys")
    print(f"🔑 Encryption Key: {encryption_key}")
    print(f"🔐 Secret Key: {secret_key}")

def print_firebase_setup_instructions():
    """Print instructions for Firebase setup."""
    print("\n" + "="*60)
    print("🔥 FIREBASE SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. Go to Firebase Console: https://console.firebase.google.com/")
    print("2. Select your project: chronolock-b9823")
    print("3. Enable the following services:")
    print("   - Authentication (Email/Password)")
    print("   - Firestore Database")
    print("   - Storage")
    print("\n4. Generate Service Account Key:")
    print("   - Go to Project Settings > Service Accounts")
    print("   - Click 'Generate New Private Key'")
    print("   - Download the JSON file")
    print("   - Extract the values and update your .env file")
    print("\n5. Update your .env file with the service account credentials:")
    print("   - FIREBASE_PRIVATE_KEY_ID")
    print("   - FIREBASE_PRIVATE_KEY")
    print("   - FIREBASE_CLIENT_EMAIL")
    print("   - FIREBASE_CLIENT_ID")
    print("   - FIREBASE_AUTH_URI")
    print("   - FIREBASE_TOKEN_URI")
    print("   - FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
    print("   - FIREBASE_CLIENT_X509_CERT_URL")
    print("\n6. Test the setup by running: python run_dev.py")
    print("="*60)

def main():
    """Main setup function."""
    print("🚀 Time Capsule Cloud - Firebase Setup")
    print("="*50)
    
    # Create .env file
    create_env_file()
    
    # Generate and update keys
    update_env_with_keys()
    
    # Print setup instructions
    print_firebase_setup_instructions()
    
    print("\n✅ Firebase configuration completed!")
    print("📝 Next steps:")
    print("   1. Complete Firebase Console setup")
    print("   2. Update .env with service account credentials")
    print("   3. Run: python run_dev.py")

if __name__ == '__main__':
    main()
