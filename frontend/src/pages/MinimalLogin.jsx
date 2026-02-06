import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Mail, Lock, Eye, EyeOff, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

const MinimalLogin = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [resetEmail, setResetEmail] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await login(email, password)
      // Don't show toast here - AuthContext already shows it
      navigate('/dashboard')
    } catch (error) {
      // Error toast already shown by AuthContext
      // Only show if there's an unexpected error
      if (!error.response) {
        toast.error('Login failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async (e) => {
    e.preventDefault()
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!resetEmail || !emailRegex.test(resetEmail)) {
      toast.error('Please enter a valid email address')
      return
    }

    setResetLoading(true)
    try {
      // Use OTP+link endpoint so email includes both code and reset link
      await authAPI.forgotPasswordOtp({ email: resetEmail })
      toast.success('Password reset code and link sent. Please check your email.')
      setShowForgotPassword(false)
      setResetEmail('')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send reset email')
    } finally {
      setResetLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4 py-12">
      {/* Background subtle gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-neutral-50 via-white to-neutral-50 opacity-50" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo/Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-block mb-6"
          >
            <div className="w-16 h-16 bg-neutral-900 rounded-2xl flex items-center justify-center mx-auto">
              <span className="text-white text-2xl font-light">TC</span>
            </div>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-4xl font-semibold text-neutral-900 mb-3 tracking-tight"
          >
            Welcome back
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-neutral-600 text-lg"
          >
            Sign in to continue
          </motion.p>
        </div>

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="luxury-card p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2.5">
                Email
              </label>
              <div className="relative">
                <Mail 
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none select-none z-10"
                  strokeWidth={1.5}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="luxury-input has-left-icon"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2.5">
                Password
              </label>
              <div className="relative">
                <Lock 
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none select-none z-10"
                  strokeWidth={1.5}
                />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="luxury-input has-left-icon has-right-icon"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 active:text-neutral-700 transition-colors z-10 p-1 -mr-1"
                  tabIndex={-1}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" strokeWidth={1.5} />
                  ) : (
                    <Eye className="w-5 h-5" strokeWidth={1.5} />
                  )}
                </button>
              </div>
              <div className="mt-2.5 text-right">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-sm text-neutral-600 hover:text-neutral-900 transition-colors underline"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.01 }}
              whileTap={{ scale: 0.99 }}
              className="luxury-button w-full"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                  />
                  Signing in...
                </span>
              ) : (
                'Sign in'
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* Sign up link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="text-center mt-8"
        >
          <p className="text-neutral-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-neutral-900 font-medium hover:underline transition-colors"
            >
              Sign up
            </Link>
          </p>
        </motion.div>
      </motion.div>

      {/* Forgot Password Modal */}
      <AnimatePresence>
        {showForgotPassword && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 px-4"
            onClick={() => setShowForgotPassword(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="luxury-card p-8 max-w-md w-full relative"
            >
              <button
                onClick={() => setShowForgotPassword(false)}
                className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
                Reset Password
              </h2>
              <p className="text-neutral-600 mb-6">
                Enter your email address and we'll send you a link to reset your password.
              </p>

              <form onSubmit={handleForgotPassword} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2.5">
                    Email
                  </label>
                  <div className="relative">
                    <Mail 
                      className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none select-none z-10"
                      strokeWidth={1.5}
                    />
                    <input
                      type="email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      required
                      className="luxury-input has-left-icon"
                      placeholder="you@example.com"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <motion.button
                    type="submit"
                    disabled={resetLoading}
                    whileHover={{ scale: resetLoading ? 1 : 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className="luxury-button flex-1"
                  >
                    {resetLoading ? (
                      <span className="flex items-center justify-center">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                        />
                        Sending...
                      </span>
                    ) : (
                      'Send Reset Link'
                    )}
                  </motion.button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotPassword(false)
                      setResetEmail('')
                    }}
                    className="luxury-button-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default MinimalLogin

