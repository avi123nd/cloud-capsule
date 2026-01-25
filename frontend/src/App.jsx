import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import MinimalLogin from './pages/MinimalLogin'
import MinimalRegister from './pages/MinimalRegister'
import MinimalDashboard from './pages/MinimalDashboard'
import MinimalCreateCapsule from './pages/MinimalCreateCapsule'
import CapsuleDetail from './pages/CapsuleDetail'
import UpdateCapsule from './pages/UpdateCapsule'
import PrivateRoute from './components/PrivateRoute'
import './App.css'
import ResetPassword from './pages/ResetPassword'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-white">
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#ffffff',
                color: '#1d1d1f',
                border: '1px solid #e5e5e5',
                borderRadius: '12px',
                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
          <Routes>
            <Route path="/login" element={<MinimalLogin />} />
            <Route path="/register" element={<MinimalRegister />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <MinimalDashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/create"
              element={
                <PrivateRoute>
                  <MinimalCreateCapsule />
                </PrivateRoute>
              }
            />
            <Route
              path="/capsule/:id"
              element={
                <PrivateRoute>
                  <CapsuleDetail />
                </PrivateRoute>
              }
            />
            <Route
              path="/capsule/:id/update"
              element={
                <PrivateRoute>
                  <UpdateCapsule />
                </PrivateRoute>
              }
            />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

