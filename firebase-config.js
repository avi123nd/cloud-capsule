// Firebase configuration for Time Capsule Cloud
// This file contains the Firebase client configuration for frontend integration

const firebaseConfig = {
  apiKey: "AIzaSyBMkN_K1ezo10I8s7cPPafMc9zELXcmMjY",
  authDomain: "chronolock-b9823.firebaseapp.com",
  projectId: "chronolock-b9823",
  storageBucket: "chronolock-b9823.firebasestorage.app",
  messagingSenderId: "1074174392161",
  appId: "1:1074174392161:web:41b66a5a89489f16043720",
  measurementId: "G-LH4F3C5Q06"
};

// Export for use in frontend applications
if (typeof module !== 'undefined' && module.exports) {
  module.exports = firebaseConfig;
} else if (typeof window !== 'undefined') {
  window.firebaseConfig = firebaseConfig;
}

// For ES6 modules
export default firebaseConfig;
