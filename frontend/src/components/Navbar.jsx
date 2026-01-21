import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, LogOut, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import CapsuleIcon3D from './3DCapsuleIcon'
import MagneticButton from './MagneticButton'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="glass sticky top-0 z-50 backdrop-blur-lg"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/dashboard" className="flex items-center space-x-2 group">
            <CapsuleIcon3D size={40} />
            <motion.span
              className="text-xl font-bold"
              style={{
                background: 'linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #fb7185, #60a5fa)',
                backgroundSize: '300% 100%',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                animation: 'gradientShift 5s ease infinite',
              }}
            >
              Time Capsule Cloud
            </motion.span>
          </Link>

          <div className="flex items-center space-x-4">
            <MagneticButton>
              <Link
                to="/create"
                className="flex items-center space-x-2 px-4 py-2 glass-strong rounded-xl hover:bg-white/20 transition-all duration-300 group relative overflow-hidden"
              >
                <motion.div
                  className="absolute inset-0 bg-white/10"
                  animate={{
                    x: ['-100%', '100%'],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                />
                <motion.div
                  animate={{
                    rotate: [0, 90, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                >
                  <Plus className="w-5 h-5 relative z-10" />
                </motion.div>
                <span className="relative z-10">Create Capsule</span>
              </Link>
            </MagneticButton>

            {user && (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 px-3 py-2 glass rounded-lg">
                  <User className="w-4 h-4 text-capsule-gold" />
                  <span className="text-sm">{user.display_name || user.email}</span>
                </div>
                <MagneticButton>
                  <motion.button
                    onClick={handleLogout}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center space-x-2 px-4 py-2 glass-strong rounded-xl hover:bg-red-500/20 transition-all duration-300 group relative overflow-hidden"
                  >
                    <motion.div
                      animate={{
                        x: [0, 4, 0],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                      }}
                    >
                      <LogOut className="w-5 h-5 relative z-10" />
                    </motion.div>
                    <span className="relative z-10">Logout</span>
                  </motion.button>
                </MagneticButton>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  )
}

export default Navbar

