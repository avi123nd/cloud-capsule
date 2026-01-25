import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'

const ResetPassword = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const t = params.get('token') || ''
    setToken(t)
  }, [location.search])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!token) {
      toast.error('Missing reset token')
      return
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      await authAPI.resetPassword({ token, new_password: newPassword })
      // Clear any existing local auth state to force sign-in
      try {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      } catch (err) {
        // ignore
      }
      toast.success('Password reset successfully. Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to reset password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="luxury-card p-8"
        >
          <h2 className="text-2xl font-semibold text-neutral-900 mb-4">Reset Password</h2>
          <p className="text-neutral-600 mb-6">Enter a new password for your account.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="luxury-input"
                placeholder="New password"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="luxury-input"
                placeholder="Confirm new password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="luxury-button w-full"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

export default ResetPassword
