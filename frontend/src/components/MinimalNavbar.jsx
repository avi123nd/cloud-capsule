import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Clock, Plus, LogOut, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const MinimalNavbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-neutral-100"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link 
            to="/dashboard" 
            className="flex items-center space-x-2 group"
            aria-label="Time Capsule Cloud Home"
          >
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6, ease: 'easeInOut' }}
            >
              <Clock className="w-6 h-6 text-neutral-900" />
            </motion.div>
            <span className="text-lg font-semibold text-neutral-900 tracking-tight">
              Time Capsule
            </span>
          </Link>

          <div className="flex items-center space-x-4">
            {user && (
              <>
                <Link
                  to="/create"
                  className="flex items-center space-x-2 px-4 py-2 text-neutral-700 hover:text-neutral-900 transition-colors duration-200 text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  <span>Create</span>
                </Link>

                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 px-3 py-2 text-sm text-neutral-600">
                    <User className="w-4 h-4" />
                    <span>{user.display_name || user.email}</span>
                  </div>
                  
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 text-sm text-neutral-600 hover:text-neutral-900 transition-colors duration-200"
                    aria-label="Logout"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  )
}

export default MinimalNavbar

