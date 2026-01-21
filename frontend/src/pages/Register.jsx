import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, Lock, User, Sparkles } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import AdvancedParticles from '../components/AdvancedParticles'
import MorphingBlobs from '../components/MorphingBlobs'
import SparkleRain from '../components/SparkleRain'
import CapsuleIcon3D from '../components/3DCapsuleIcon'

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    displayName: '',
  })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const result = await register(formData.email, formData.password, formData.displayName)
    setLoading(false)

    if (result.success) {
      navigate('/dashboard')
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <MorphingBlobs />
      <AdvancedParticles count={150} />
      <SparkleRain count={50} />
      
      {/* Grid overlay */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(212, 175, 55, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
        }} />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 w-full max-w-md px-6"
      >
        <motion.div variants={itemVariants} className="text-center mb-8">
          <motion.div
            whileHover={{ scale: 1.2, rotateZ: 360 }}
            transition={{ duration: 0.8, type: 'spring' }}
            className="inline-block mb-6"
          >
            <CapsuleIcon3D size={120} />
          </motion.div>
          <motion.h1 
            className="text-5xl font-bold mb-3"
            animate={{
              backgroundPosition: ['0%', '100%', '0%'],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'linear',
            }}
            style={{
              background: 'linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #fb7185, #60a5fa)',
              backgroundSize: '300% 100%',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Create Account
          </motion.h1>
          <motion.p 
            className="text-xl text-gray-300 glow-text"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            Start preserving your memories
          </motion.p>
        </motion.div>

        <motion.form
          variants={itemVariants}
          onSubmit={handleSubmit}
          className="glass-strong rounded-3xl p-10 shadow-2xl space-y-6 relative overflow-hidden card-3d"
          whileHover={{ scale: 1.02 }}
          style={{
            backdropFilter: 'blur(20px)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 60px rgba(212, 175, 55, 0.2)',
          }}
        >
          {/* Shine effect overlay */}
          <div className="absolute inset-0 shine-effect pointer-events-none" />
          <motion.div variants={itemVariants} className="space-y-2">
            <label className="flex items-center space-x-2 text-sm font-medium">
              <User className="w-4 h-4 text-capsule-gold" />
              <span>Display Name</span>
            </label>
            <input
              type="text"
              name="displayName"
              value={formData.displayName}
              onChange={handleChange}
              className="w-full px-4 py-3 glass rounded-lg focus:outline-none focus:ring-2 focus:ring-capsule-gold transition-all"
              placeholder="Your Name"
            />
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-2">
            <label className="flex items-center space-x-2 text-sm font-medium">
              <Mail className="w-4 h-4 text-capsule-gold" />
              <span>Email</span>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 glass rounded-lg focus:outline-none focus:ring-2 focus:ring-capsule-gold transition-all"
              placeholder="your@email.com"
            />
          </motion.div>

          <motion.div variants={itemVariants} className="space-y-2">
            <label className="flex items-center space-x-2 text-sm font-medium">
              <Lock className="w-4 h-4 text-capsule-gold" />
              <span>Password</span>
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 glass rounded-lg focus:outline-none focus:ring-2 focus:ring-capsule-gold transition-all"
              placeholder="••••••••"
            />
            <p className="text-xs text-gray-400">
              At least 8 characters with uppercase, lowercase, and number
            </p>
          </motion.div>

          <motion.button
            variants={itemVariants}
            type="submit"
            disabled={loading}
            whileHover={{ 
              scale: 1.05,
              boxShadow: '0 0 30px rgba(212, 175, 55, 0.8)',
            }}
            whileTap={{ scale: 0.95 }}
            className="w-full py-4 bg-gradient-to-r from-capsule-gold via-yellow-400 to-capsule-gold text-black font-bold rounded-xl hover:shadow-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 relative overflow-hidden group"
            style={{
              backgroundSize: '200% 100%',
              animation: 'gradientShift 3s ease infinite',
            }}
          >
            <motion.div
              className="absolute inset-0 bg-white/20"
              animate={{
                x: ['-100%', '100%'],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
            {loading ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-black border-t-transparent rounded-full relative z-10"
                />
                <span className="relative z-10">Creating...</span>
              </>
            ) : (
              <>
                <motion.div
                  animate={{ 
                    rotate: [0, 10, -10, 0],
                    scale: [1, 1.2, 1],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Sparkles className="w-5 h-5 relative z-10" />
                </motion.div>
                <span className="relative z-10">Create Account</span>
              </>
            )}
          </motion.button>

          <motion.div variants={itemVariants} className="text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-capsule-gold hover:text-yellow-400 font-medium transition-colors"
              >
                Sign in
              </Link>
            </p>
          </motion.div>
        </motion.form>
      </motion.div>
    </div>
  )
}

export default Register

