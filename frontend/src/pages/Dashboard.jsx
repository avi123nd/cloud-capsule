import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import { Plus, Clock, Lock, Unlock, Calendar, FileText, Image, Video, Trash2, Download } from 'lucide-react'
import { format, differenceInDays } from 'date-fns'
import Navbar from '../components/Navbar'
import MorphingBlobs from '../components/MorphingBlobs'
import AdvancedParticles from '../components/AdvancedParticles'
import MagneticButton from '../components/MagneticButton'
import { capsuleAPI, dashboardAPI } from '../services/api'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [capsules, setCapsules] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, locked, unlocked

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [capsulesRes, statsRes] = await Promise.all([
        capsuleAPI.getAll({ include_locked: true }),
        dashboardAPI.getStats(),
      ])
      setCapsules(capsulesRes.data.capsules)
      setStats(statsRes.data.statistics)
    } catch (error) {
      toast.error('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this capsule?')) return
    
    try {
      await capsuleAPI.delete(id)
      toast.success('Capsule deleted')
      loadData()
    } catch (error) {
      toast.error('Failed to delete capsule')
    }
  }

  const handleDownload = async (id) => {
    try {
      const response = await capsuleAPI.download(id)
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const capsule = capsules.find(c => c.capsule_id === id)
      a.download = capsule?.filename || 'capsule'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Download started')
    } catch (error) {
      toast.error('Failed to download')
    }
  }

  const getFileIcon = (type) => {
    switch (type) {
      case 'text': return <FileText className="w-6 h-6" />
      case 'image': return <Image className="w-6 h-6" />
      case 'video': return <Video className="w-6 h-6" />
      default: return <FileText className="w-6 h-6" />
    }
  }

  const filteredCapsules = capsules.filter(c => {
    if (filter === 'locked') return !c.is_unlocked
    if (filter === 'unlocked') return c.is_unlocked
    return true
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-16 h-16 border-t-4 border-b-4 border-capsule-gold rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20 relative overflow-hidden">
      <MorphingBlobs />
      <AdvancedParticles count={100} />
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={<Clock className="w-6 h-6" />}
              label="Total Capsules"
              value={stats.total_capsules}
              color="from-blue-500 to-cyan-500"
              index={0}
            />
            <StatCard
              icon={<Lock className="w-6 h-6" />}
              label="Locked"
              value={stats.locked_capsules}
              color="from-purple-500 to-pink-500"
              index={1}
            />
            <StatCard
              icon={<Unlock className="w-6 h-6" />}
              label="Unlocked"
              value={stats.unlocked_capsules}
              color="from-green-500 to-emerald-500"
              index={2}
            />
            <StatCard
              icon={<Calendar className="w-6 h-6" />}
              label="Upcoming"
              value={stats.upcoming_unlocks}
              color="from-yellow-500 to-orange-500"
              index={3}
            />
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <motion.h1
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="text-4xl font-bold glow-text"
            style={{
              background: 'linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #fb7185, #60a5fa)',
              backgroundSize: '300% 100%',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              animation: 'gradientShift 5s ease infinite',
            }}
          >
            Your Time Capsules
          </motion.h1>
          <Link to="/create">
            <MagneticButton>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-capsule-gold via-yellow-400 to-capsule-gold text-black font-bold rounded-xl hover:shadow-2xl transition-all relative overflow-hidden group"
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
                <motion.div
                  animate={{
                    rotate: [0, 90, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: 0.5,
                  }}
                >
                  <Plus className="w-5 h-5 relative z-10" />
                </motion.div>
                <span className="relative z-10">New Capsule</span>
              </motion.button>
            </MagneticButton>
          </Link>
        </div>

        {/* Filters */}
        <div className="flex space-x-2 mb-6">
          {['all', 'locked', 'unlocked'].map((f) => (
            <motion.button
              key={f}
              onClick={() => setFilter(f)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === f
                  ? 'glass-strong text-capsule-gold'
                  : 'glass text-gray-300 hover:text-white'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </motion.button>
          ))}
        </div>

        {/* Capsules Grid */}
        {filteredCapsules.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <Clock className="w-20 h-20 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400 text-xl">No capsules found</p>
            <Link to="/create">
              <motion.button
                whileHover={{ scale: 1.05 }}
                className="mt-4 px-6 py-2 glass-strong rounded-lg"
              >
                Create Your First Capsule
              </motion.button>
            </Link>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {filteredCapsules.map((capsule, index) => (
                <CapsuleCard
                  key={capsule.capsule_id}
                  capsule={capsule}
                  index={index}
                  onDelete={handleDelete}
                  onDownload={handleDownload}
                  getFileIcon={getFileIcon}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  )
}

const StatCard = ({ icon, label, value, color, index }) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setMousePosition({
      x: (e.clientX - rect.left - rect.width / 2) / 10,
      y: (e.clientY - rect.top - rect.height / 2) / 10,
    })
  }

  return (
    <motion.div
      initial={{ scale: 0, rotateY: -90, opacity: 0 }}
      animate={{ scale: 1, rotateY: 0, opacity: 1 }}
      transition={{ delay: index * 0.1, type: 'spring', stiffness: 100 }}
      whileHover={{ 
        scale: 1.05,
        rotateY: mousePosition.x,
        rotateX: -mousePosition.y,
        z: 50,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setMousePosition({ x: 0, y: 0 })}
      className={`glass-strong rounded-2xl p-6 bg-gradient-to-br ${color} card-3d relative overflow-hidden`}
      style={{
        transformStyle: 'preserve-3d',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
      }}
    >
      {/* Shine effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
          delay: index * 0.5,
        }}
      />
      <div className="flex items-center justify-between relative z-10">
        <div>
          <p className="text-white/80 text-sm mb-1 font-medium">{label}</p>
          <motion.p
            className="text-4xl font-bold text-white"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: index * 0.2,
            }}
          >
            {value}
          </motion.p>
        </div>
        <motion.div
          className="text-white/80"
          animate={{ 
            rotate: [0, 10, -10, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: index * 0.3,
          }}
        >
          {icon}
        </motion.div>
      </div>
    </motion.div>
  )
}

const CapsuleCard = ({ capsule, index, onDelete, onDownload, getFileIcon }) => {
  const unlockDate = new Date(capsule.unlock_date)
  const now = new Date()
  const daysUntil = differenceInDays(unlockDate, now)
  const isUnlocked = capsule.is_unlocked
  const isPast = now > unlockDate
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setMousePosition({
      x: (e.clientX - rect.left - rect.width / 2) / 20,
      y: (e.clientY - rect.top - rect.height / 2) / 20,
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, rotateX: -20 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      exit={{ opacity: 0, scale: 0.8, rotateZ: -10 }}
      transition={{ 
        delay: index * 0.05,
        type: 'spring',
        stiffness: 100,
      }}
      whileHover={{ 
        y: -10,
        rotateY: mousePosition.x,
        rotateX: -mousePosition.y,
        scale: 1.02,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setMousePosition({ x: 0, y: 0 })}
      className="glass-strong rounded-2xl p-6 cursor-pointer capsule-glow group card-3d relative overflow-hidden"
      style={{
        transformStyle: 'preserve-3d',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2), 0 0 20px rgba(212, 175, 55, 0.1)',
      }}
    >
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `linear-gradient(135deg, ${
            capsule.capsule_type === 'text' ? 'rgba(59, 130, 246, 0.1)' :
            capsule.capsule_type === 'image' ? 'rgba(147, 51, 234, 0.1)' :
            'rgba(236, 72, 153, 0.1)'
          }, transparent)`,
        }}
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
      
      {/* Shine effect */}
      <motion.div
        className="absolute inset-0 shine-effect opacity-0 group-hover:opacity-100 transition-opacity"
      />
      <Link to={`/capsule/${capsule.capsule_id}`} className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <motion.div
            className={`p-3 rounded-xl ${
              capsule.capsule_type === 'text' ? 'bg-blue-500/20' :
              capsule.capsule_type === 'image' ? 'bg-purple-500/20' :
              'bg-pink-500/20'
            }`}
            whileHover={{ rotate: 360, scale: 1.2 }}
            transition={{ duration: 0.5 }}
          >
            {getFileIcon(capsule.capsule_type)}
          </motion.div>
          {isUnlocked ? (
            <motion.span
              className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full font-medium"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Unlocked
            </motion.span>
          ) : (
            <motion.span
              className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full font-medium"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Locked
            </motion.span>
          )}
        </div>

        <motion.h3
          className="text-lg font-bold mb-2 group-hover:text-capsule-gold transition-colors glow-text"
          whileHover={{ scale: 1.05 }}
        >
          {capsule.filename}
        </motion.h3>

        {capsule.description && (
          <p className="text-gray-400 text-sm mb-4 line-clamp-2">{capsule.description}</p>
        )}

        <div className="flex items-center space-x-2 text-xs text-gray-400 mb-4">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          >
            <Calendar className="w-4 h-4" />
          </motion.div>
          <span>
            {isUnlocked ? 'Unlocked' : isPast ? 'Ready' : `${daysUntil} days left`}
          </span>
        </div>

        <div className="text-xs text-gray-500">
          {format(new Date(capsule.created_at), 'MMM dd, yyyy')}
        </div>
      </Link>

      <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-white/10 relative z-10">
        {isUnlocked && (
          <MagneticButton>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation()
                onDownload(capsule.capsule_id)
              }}
              className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 glass rounded-lg hover:bg-white/20 transition-all relative overflow-hidden group"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/20"
                animate={{ x: ['-100%', '100%'] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              />
              <motion.div
                animate={{ y: [0, -2, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Download className="w-4 h-4 relative z-10" />
              </motion.div>
              <span className="relative z-10">Download</span>
            </motion.button>
          </MagneticButton>
        )}
        <MagneticButton>
          <motion.button
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => {
              e.stopPropagation()
              onDelete(capsule.capsule_id)
            }}
            className="px-3 py-2 glass rounded-lg hover:bg-red-500/20 transition-all"
          >
            <Trash2 className="w-4 h-4 text-red-400" />
          </motion.button>
        </MagneticButton>
      </div>
    </motion.div>
  )
}

export default Dashboard

