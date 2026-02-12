import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const MinimalRegister = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    display_name: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    // Client-side validation
    if (!formData.display_name || formData.display_name.trim() === '') {
      toast.error('Display name is required')
      setLoading(false)
      return
    }
    
    if (!formData.email || formData.email.trim() === '') {
      toast.error('Email is required')
      setLoading(false)
      return
    }
    
    if (!formData.password || formData.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      setLoading(false)
      return
    }

    try {
      await register(formData.email, formData.password, formData.display_name)
      toast.success('Account created successfully')
      navigate('/dashboard')
    } catch (error) {
      // Debug: Log the full error to console (remove in production)
      console.error('Registration error:', error)
      console.error('Error response:', error.response)
      console.error('Error data:', error.response?.data)
      
      // Check if it's a network error (no response from server)
      if (!error.response) {
        // Network error - server might be down or unreachable
        const isNetworkError = error.message && (
          error.message.includes('Network Error') || 
          error.message.includes('ERR_NETWORK') ||
          error.message.includes('Failed to fetch') ||
          error.code === 'ERR_NETWORK'
        )
        
        if (isNetworkError) {
          toast.error('Network error: Unable to connect to server. Please check your connection and try again.')
        } else {
          toast.error(error.message || 'Network error: Unable to connect to server.')
        }
        return
      }
      
      // API error - server responded with an error
      const statusCode = error.response?.status
      let errorMessage = 'Registration failed'
      
      // Try to get error message from different possible locations
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      } else if (error.message) {
        errorMessage = error.message
      }
      
      // Show user-friendly message for different error types
      if (statusCode === 400) {
        // Bad request - validation errors
        if (errorMessage.includes('email')) {
          toast.error('Please enter a valid email address')
        } else if (errorMessage.includes('password')) {
          toast.error('Password must be at least 8 characters with uppercase, lowercase, and number')
        } else if (errorMessage.includes('Display name')) {
          toast.error(errorMessage)
        } else {
          toast.error(errorMessage)
        }
      } else if (statusCode === 409) {
        // Conflict - duplicate email or display name
        const lowerMessage = errorMessage.toLowerCase()
        if (lowerMessage.includes('email') || 
            lowerMessage.includes('already exists') ||
            lowerMessage.includes('already registered') ||
            lowerMessage.includes('account with this email')) {
          toast.error('An account with this email already exists. Please use a different email or sign in.')
        } else {
          toast.error(errorMessage)
        }
      } else {
        toast.error(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4 py-12">
      <div className="absolute inset-0 bg-gradient-to-br from-neutral-50 via-white to-neutral-50 opacity-50" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="w-full max-w-md relative z-10"
      >
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
            Create account
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-neutral-600 text-lg"
          >
            Start preserving your memories
          </motion.p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="luxury-card p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2.5">
                Display Name
              </label>
              <div className="relative">
                <User 
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none select-none z-10"
                  strokeWidth={1.5}
                />
                <input
                  type="text"
                  name="display_name"
                  value={formData.display_name}
                  onChange={handleChange}
                  required
                  className="luxury-input has-left-icon"
                  placeholder="Your name"
                />
              </div>
            </div>

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
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
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
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
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
              <p className="text-xs text-neutral-500 mt-2.5">
                At least 8 characters with uppercase, lowercase, and number
              </p>
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
                  Creating...
                </span>
              ) : (
                'Create account'
              )}
            </motion.button>
          </form>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="text-center mt-8"
        >
          <p className="text-neutral-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-neutral-900 font-medium hover:underline transition-colors"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default MinimalRegister

