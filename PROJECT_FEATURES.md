# Time Capsule Cloud - Project Features

## Overview
A secure time capsule cloud application built with Python Flask backend that allows users to store encrypted files and unlock them at a specified future date. The application uses MongoDB for data storage, GridFS for file storage, and implements robust security features.

---

## 🔐 Authentication & Security Features

### User Authentication
- **Email/Password Registration**: Users can register with email and password
- **User Login**: Secure login with email/password authentication
- **JWT Token Authentication**: Stateless JWT-based authentication (7-day token expiry)
- **Password Hashing**: Passwords are securely hashed using bcrypt
- **Email Validation**: Case-insensitive email handling with duplicate checking
- **Display Name Support**: Optional display name during registration
- **User Profile Retrieval**: Get authenticated user profile information

### Security Measures
- **AES-256 Encryption**: All capsule files are encrypted using AES-256 in CBC mode
- **Unique IV per File**: Each encrypted file uses a random initialization vector
- **Secure File Storage**: Encrypted files stored in MongoDB GridFS
- **Authorization Middleware**: Protected routes require valid JWT tokens
- **File Size Limits**: Maximum file size of 100MB per upload
- **File Type Validation**: Only allowed file extensions accepted

---

## 📦 Capsule Management Features

### Capsule Creation
- **File Upload**: Upload text, PDF, image, or video files
- **Unlock Date Setting**: Set a future date/time for automatic unlock
- **Capsule Description**: Optional description for each capsule
- **Automatic File Type Detection**: Automatically categorizes files (text, image, video)
- **Capsule ID Generation**: Unique UUID for each capsule
- **Metadata Storage**: Complete metadata stored in MongoDB

### Capsule Retrieval
- **List All Capsules**: Get all user's capsules (with optional filter for locked/unlocked)
- **Get Single Capsule**: Retrieve metadata for a specific capsule
- **Filter by Lock Status**: Option to include or exclude locked capsules
- **Sorted Results**: Capsules sorted by creation date (newest first)

### Capsule Unlocking
- **Manual Unlock**: Unlock a capsule when unlock date has passed
- **Automatic Unlock**: Scheduled automatic unlocking via background scheduler
- **Unlock Date Validation**: Prevents unlocking before the specified date
- **Decryption on Unlock**: Files are automatically decrypted when unlocked
- **Unlock Timestamp**: Records when each capsule was unlocked
- **Base64 Encoding**: Unlocked binary files returned as base64 strings

---

## 📊 Dashboard Features

### Statistics & Analytics
- **Total Capsules Count**: Total number of capsules per user
- **Locked Capsules Count**: Count of capsules still locked
- **Unlocked Capsules Count**: Count of capsules that have been unlocked
- **Upcoming Unlocks**: Capsules unlocking within the next 7 days
- **Capsule Type Breakdown**: Statistics by file type (text, image, video, other)

### Dashboard Views
- **Main Dashboard**: Comprehensive view with statistics and capsule lists
- **Unlocked Capsules View**: Filter to view only unlocked capsules
- **Upcoming Unlocks View**: View capsules scheduled to unlock soon
- **Statistics Endpoint**: Get detailed statistics without full capsule data

---

## ⏰ Scheduling Features

### Automatic Unlocking
- **Daily Scheduler**: Daily check at midnight (00:00) for capsules ready to unlock
- **Hourly Scheduler**: Hourly check for more timely unlocks
- **Background Processing**: Unlocks happen in background without user intervention
- **Automatic Decryption**: Files automatically decrypted when unlock date arrives
- **Scheduler Status**: Ability to check scheduler status and jobs
- **Error Logging**: Failed unlock attempts are logged for debugging

---

## 💾 Storage Features

### Database Storage
- **MongoDB Integration**: Uses MongoDB for metadata and user data
- **GridFS Storage**: Large files stored in MongoDB GridFS
- **Collection Management**: Separate collections for users and capsules
- **Indexing**: Efficient queries with proper indexing

### File Handling
- **Multiple File Types**: Supports txt, pdf, png, jpg, jpeg, gif, mp4, avi, mov
- **Secure Filename Handling**: Filenames sanitized for security
- **Original Size Tracking**: Tracks original file size before encryption
- **Content Type Management**: Proper content type handling for GridFS

---

## 🛠️ API Features

### REST API Endpoints

#### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile (protected)

#### Capsule Endpoints
- `POST /capsules` - Create a new capsule (protected)
- `GET /capsules` - List user's capsules (protected)
- `GET /capsules/<id>` - Get capsule metadata (protected)
- `POST /capsules/<id>/unlock` - Unlock a capsule (protected)
- `GET /capsules/<id>/metadata` - Get capsule metadata (protected)

#### Dashboard Endpoints
- `GET /dashboard` - Main dashboard with statistics (protected)
- `GET /dashboard/unlocked` - Get unlocked capsules (protected)
- `GET /dashboard/upcoming` - Get upcoming unlocks (protected)
- `GET /dashboard/stats` - Get statistics only (protected)

#### System Endpoints
- `GET /health` - Health check endpoint

### API Features
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **JSON Responses**: All endpoints return JSON responses
- **Request Validation**: Input validation for all endpoints
- **ISO Date Format**: Date/time handling in ISO 8601 format

---

## 🧪 Testing Features

### Test Suite
- **Unit Tests**: Tests for authentication service
- **Capsule Service Tests**: Tests for capsule creation and management
- **Encryption Service Tests**: Tests for encryption/decryption functionality
- **Test Configuration**: Separate testing configuration
- **Pytest Framework**: Uses pytest for testing

---

## 🔧 Development Features

### Development Tools
- **Development Server**: Separate development startup script
- **Environment Configuration**: Environment variable management with `.env` files
- **Environment Validation**: Startup checks for required environment variables
- **Debug Mode**: Flask debug mode for development
- **Logging**: Comprehensive logging for debugging
- **Hot Reload**: Automatic reload on code changes

### Configuration Management
- **Environment-Based Config**: Different configurations for development, production, testing
- **Secrets Management**: Secure handling of JWT secrets and encryption keys
- **Config Validation**: Validation of encryption key length and other settings

---

## 🚀 Infrastructure Features

### Server Features
- **Flask Application**: Python Flask web framework
- **Port Configuration**: Configurable port (default 5000)
- **Host Binding**: Configurable host binding
- **Error Handlers**: Custom error handlers for 400, 413, 500 errors

### Production Features
- **Production Configuration**: Separate production configuration class
- **Logging to Files**: Rotating file handler for production logs
- **Log Rotation**: Automatic log rotation with size limits

---

## 📝 Additional Features

### Documentation
- **README**: Comprehensive project documentation
- **Quick Start Guide**: Step-by-step setup instructions
- **API Documentation**: Documented endpoints and usage
- **Code Comments**: Well-documented code with docstrings

### File Structure
- **Modular Architecture**: Organized into routes, services, and tests
- **Blueprint Pattern**: Flask blueprints for route organization
- **Service Layer**: Separation of concerns with service classes
- **Clean Code**: Well-structured and maintainable codebase

---

## 🔄 Data Flow Features

1. **Registration Flow**: User registers → Password hashed → User stored → JWT token returned
2. **Login Flow**: User logs in → Credentials verified → JWT token returned
3. **Capsule Creation Flow**: File uploaded → Encrypted → Stored in GridFS → Metadata saved
4. **Unlock Flow**: Unlock date reached → File retrieved → Decrypted → Returned to user

---

## Summary

This is a comprehensive time capsule application with:
- **12+ API endpoints** for complete functionality
- **Multiple security layers** (encryption, hashing, JWT)
- **Automatic scheduling** for timely unlocks
- **Rich dashboard** with statistics and analytics
- **Production-ready** architecture with proper error handling
- **Developer-friendly** with comprehensive documentation and testing


