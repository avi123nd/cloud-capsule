# Time Capsule Cloud - Backend with MongoDB

A secure time capsule app using Python, Flask, MongoDB, GridFS, and JWT auth.

## Features
- Email/password user registration & login (hashed passwords)
- JWT stateless authentication
- Store encrypted files (text, image, video) in MongoDB GridFS
- Capsules and metadata managed via MongoDB collections
- AES-256 encryption for all capsule data
- Daily scheduler (APScheduler) for automatic unlock processing

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy `env.example` to `.env` and fill in:
```
MONGO_URI=mongodb://localhost:27017/timecapsule
JWT_SECRET=your-very-secure-jwt-secret
ENCRYPTION_KEY=32-char-random-hex-string-or-base64
SECRET_KEY=flask-session-key
```

### 3. Start the API
```bash
python run_dev.py
```
API at http://localhost:5000

## API Endpoints (JWT auth required after login)
- POST /auth/register
- POST /auth/login
- GET /auth/profile
- POST /capsules
- GET /capsules
- GET /capsules/<id>
- POST /capsules/<id>/unlock

## Security
- Passwords: hashed with bcrypt
- Files: AES-256 encrypted before storage
- Use strong JWT and encryption secrets in .env!

## Testing
```bash
pytest tests/
```


For more, see comments in code and docstrings throughout the codebase.
