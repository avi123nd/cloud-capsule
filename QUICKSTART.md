# Time Capsule Cloud - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Firebase
```bash
python setup_firebase.py
```

### 3. Complete Firebase Console Setup
1. Go to [Firebase Console](https://console.firebase.google.com/project/chronolock-b9823)
2. Enable these services:
   - **Authentication** → Sign-in method → Email/Password → Enable
   - **Firestore Database** → Create database → Start in test mode
   - **Storage** → Get started → Start in test mode

### 4. Get Service Account Credentials
1. In Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Download the JSON file
4. Copy the values to your `.env` file:
   ```env
   FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@chronolock-b9823.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your-client-id
   FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
   FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
   FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
   FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...
   ```

### 5. Start the Server
```bash
python run_dev.py
```

## 🧪 Test the API

### Health Check
```bash
curl http://localhost:5000/health
```

### Create a Test User (Frontend)
Use Firebase Auth in your frontend to create a user, then use the ID token for API calls.

### Create a Test Capsule
```bash
curl -X POST http://localhost:5000/capsules \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -F "file=@test.txt" \
  -F "unlock_date=2024-12-31T23:59:59Z" \
  -F "description=Test capsule"
```

## 📱 Frontend Integration

Use the Firebase config in your frontend:

```javascript
// firebase-config.js
const firebaseConfig = {
  apiKey: "AIzaSyBMkN_K1ezo10I8s7cPPafMc9zELXcmMjY",
  authDomain: "chronolock-b9823.firebaseapp.com",
  projectId: "chronolock-b9823",
  storageBucket: "chronolock-b9823.firebasestorage.app",
  messagingSenderId: "1074174392161",
  appId: "1:1074174392161:web:41b66a5a89489f16043720",
  measurementId: "G-LH4F3C5Q06"
};
```

## 🔧 Troubleshooting

### Common Issues:

1. **Firebase not initialized**: Check your service account credentials in `.env`
2. **Permission denied**: Ensure Firestore and Storage rules allow your service account
3. **Encryption errors**: Verify your `ENCRYPTION_KEY` is exactly 32 characters

### Test Commands:
```bash
# Run tests
python run_tests.py

# Check environment
python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"
```

## 📚 Next Steps

1. **Frontend Development**: Use the Firebase config to build your React/Vue.js frontend
2. **Authentication**: Implement Firebase Auth in your frontend
3. **File Upload**: Create a file upload component
4. **Dashboard**: Build a user dashboard to view capsules
5. **Real-time Updates**: Add real-time notifications for capsule unlocks

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review the API endpoints in the routes files
- Test individual services with the unit tests
- Check Firebase Console for any configuration issues
