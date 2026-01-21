import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Clock, Lock, Unlock, Calendar, FileText, Image, Video, Trash2, Download, Filter } from 'lucide-react'
import { format, differenceInDays } from 'date-fns'
import MinimalNavbar from '../components/MinimalNavbar'
import { capsuleAPI, dashboardAPI } from '../services/api'
import toast from 'react-hot-toast'

const MinimalDashboard = () => {
  const [capsules, setCapsules] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const errorShownRef = useRef(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [capsulesRes, statsRes] = await Promise.all([
        capsuleAPI.getAll({ include_locked: 'true' }),
        dashboardAPI.getStats(),
      ])
      setCapsules(capsulesRes.data.capsules || [])
      setStats(statsRes.data)
      errorShownRef.current = false // Reset on success
    } catch (error) {
      // Only show error if it's not a 401 (unauthorized) - that's handled by interceptor
      // And only show once to prevent duplicate toasts (React StrictMode runs twice in dev)
      if (error.response?.status !== 401 && !errorShownRef.current) {
        const errorMessage = error.response?.data?.error || error.message || 'Failed to load data'
        toast.error(errorMessage)
        errorShownRef.current = true // Mark as shown
      }
    } finally {
      setLoading(false)
    }
  }

  const filteredCapsules = capsules.filter((c) => {
    if (filter === 'locked') return !c.is_unlocked
    if (filter === 'unlocked') return c.is_unlocked
    return true
  })

  const getFileIcon = (type) => {
    switch (type) {
      case 'image':
        return <Image className="w-5 h-5" />
      case 'video':
        return <Video className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this capsule?')) return
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
      const response = await capsuleAPI.get(`/capsules/${id}/download`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', response.headers['content-disposition']?.split('filename=')[1] || 'capsule')
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Download started')
    } catch (error) {
      toast.error('Failed to download capsule')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-8 h-8 border-2 border-neutral-300 border-t-neutral-900 rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <MinimalNavbar />

      {/* Hero Section */}
      <section className="relative bg-white border-b border-neutral-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-24 lg:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-5xl lg:text-6xl font-semibold text-neutral-900 mb-6 tracking-tight">
              Your Time Capsules
            </h1>
            <p className="text-xl text-neutral-600 mb-8 leading-relaxed">
              Preserve your memories and messages for the future. Lock them away and rediscover them when the time is right.
            </p>
            <Link to="/create">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="luxury-button inline-flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Create New Capsule</span>
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      {stats && (
        <section className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <StatCard
              icon={<Clock className="w-5 h-5" />}
              label="Total"
              value={stats.total_capsules}
              index={0}
            />
            <StatCard
              icon={<Lock className="w-5 h-5" />}
              label="Locked"
              value={stats.locked_capsules}
              index={1}
            />
            <StatCard
              icon={<Unlock className="w-5 h-5" />}
              label="Unlocked"
              value={stats.unlocked_capsules}
              index={2}
            />
            <StatCard
              icon={<Calendar className="w-5 h-5" />}
              label="Upcoming"
              value={stats.upcoming_unlocks}
              index={3}
            />
          </div>
        </section>
      )}

      {/* Capsules Section */}
      <section className="max-w-7xl mx-auto px-6 lg:px-8 pb-24">
        {/* Filters */}
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold text-neutral-900">Your Capsules</h2>
          <div className="flex items-center space-x-2">
            {['all', 'locked', 'unlocked'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  filter === f
                    ? 'bg-neutral-900 text-white'
                    : 'bg-white text-neutral-600 hover:bg-neutral-100 border border-neutral-200'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Capsules Grid */}
        {filteredCapsules.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-neutral-400" />
            </div>
            <p className="text-neutral-600 text-lg mb-4">No capsules yet</p>
            <Link to="/create">
              <button className="luxury-button-secondary">
                Create your first capsule
              </button>
            </Link>
          </div>
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
      </section>
    </div>
  )
}

const StatCard = ({ icon, label, value, index }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.1, duration: 0.5 }}
    className="luxury-card p-6 text-center"
  >
    <div className="text-neutral-400 mb-2 flex justify-center">{icon}</div>
    <p className="text-3xl font-semibold text-neutral-900 mb-1">{value}</p>
    <p className="text-sm text-neutral-600">{label}</p>
  </motion.div>
)

const CapsuleCard = ({ capsule, index, onDelete, onDownload, getFileIcon }) => {
  const unlockDate = new Date(capsule.unlock_date)
  const now = new Date()
  const daysUntil = differenceInDays(unlockDate, now)
  const isUnlocked = capsule.is_unlocked

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
      className="luxury-card p-6 group"
    >
      <Link to={`/capsule/${capsule.capsule_id}`} className="block mb-4">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 bg-neutral-100 rounded-xl">
            {getFileIcon(capsule.capsule_type)}
          </div>
          {isUnlocked ? (
            <span className="px-3 py-1 bg-green-50 text-green-700 text-xs rounded-full font-medium">
              Unlocked
            </span>
          ) : (
            <span className="px-3 py-1 bg-yellow-50 text-yellow-700 text-xs rounded-full font-medium">
              Locked
            </span>
          )}
        </div>

        <h3 className="text-lg font-semibold text-neutral-900 mb-2 line-clamp-1">
          {capsule.filename}
        </h3>

        {capsule.description && (
          <p className="text-sm text-neutral-600 mb-4 line-clamp-2">
            {capsule.description}
          </p>
        )}

        <div className="flex items-center space-x-2 text-xs text-neutral-500">
          <Calendar className="w-4 h-4" />
          <span>
            {isUnlocked ? 'Unlocked' : `${daysUntil} days left`}
          </span>
        </div>
      </Link>

      <div className="flex items-center space-x-2 pt-4 border-t border-neutral-100">
        {isUnlocked && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDownload(capsule.capsule_id)
            }}
            className="flex-1 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>
        )}
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete(capsule.capsule_id)
          }}
          className="px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  )
}

export default MinimalDashboard

