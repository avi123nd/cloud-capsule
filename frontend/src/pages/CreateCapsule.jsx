import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, Calendar, FileText, X, Sparkles } from 'lucide-react'
import { format } from 'date-fns'
import Navbar from '../components/Navbar'
import MorphingBlobs from '../components/MorphingBlobs'
import AdvancedParticles from '../components/AdvancedParticles'
import MagneticButton from '../components/MagneticButton'
import { capsuleAPI } from '../services/api'
import toast from 'react-hot-toast'

const CreateCapsule = () => {
  const [file, setFile] = useState(null)
  const [unlockDate, setUnlockDate] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      toast.error('Please select a file')
      return
    }

    if (!unlockDate) {
      toast.error('Please select an unlock date')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('unlock_date', new Date(unlockDate).toISOString())
      formData.append('description', description)

      await capsuleAPI.create(formData)
      toast.success('Capsule created successfully!')
      navigate('/dashboard')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create capsule')
    } finally {
      setLoading(false)
    }
  }

  const getTomorrowDate = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().slice(0, 16)
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <MorphingBlobs />
      <AdvancedParticles count={100} />
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20, rotateX: -10 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          className="glass-strong rounded-3xl p-10 card-3d relative overflow-hidden"
          style={{
            backdropFilter: 'blur(20px)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 60px rgba(212, 175, 55, 0.2)',
          }}
        >
          <div className="absolute inset-0 shine-effect pointer-events-none" />
          <motion.h1
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="text-4xl font-bold mb-8 glow-text relative z-10"
            style={{
              background: 'linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #fb7185, #60a5fa)',
              backgroundSize: '300% 100%',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              animation: 'gradientShift 5s ease infinite',
            }}
          >
            Create New Time Capsule
          </motion.h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Upload */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <label className="block text-sm font-medium mb-2">File</label>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
                  dragActive
                    ? 'border-capsule-gold bg-capsule-gold/20 shadow-[0_0_30px_rgba(212,175,55,0.5)] scale-105'
                    : 'border-gray-600 hover:border-gray-500 hover:shadow-lg'
                }`}
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  accept=".txt,.pdf,.png,.jpg,.jpeg,.gif,.mp4,.avi,.mov"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  {file ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-center space-x-2">
                        <FileText className="w-8 h-8 text-capsule-gold" />
                        <span className="font-medium">{file.name}</span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            setFile(null)
                          }}
                          className="ml-2 text-red-400 hover:text-red-300"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <motion.div
                        whileHover={{ scale: 1.2, rotate: 360 }}
                        animate={{ 
                          y: [0, -10, 0],
                          rotate: [0, 5, -5, 0],
                        }}
                        transition={{
                          y: { duration: 2, repeat: Infinity },
                          rotate: { duration: 3, repeat: Infinity },
                        }}
                        className="inline-block"
                      >
                        <Upload className="w-16 h-16 text-capsule-gold mx-auto" />
                      </motion.div>
                      <div>
                        <p className="text-gray-300">
                          Drag and drop your file here, or{' '}
                          <span className="text-capsule-gold font-medium">click to browse</span>
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                          Supports: txt, pdf, png, jpg, gif, mp4, avi, mov (Max 100MB)
                        </p>
                      </div>
                    </div>
                  )}
                </label>
              </div>
            </motion.div>

            {/* Unlock Date */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <label className="block text-sm font-medium mb-2 flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-capsule-gold" />
                <span>Unlock Date</span>
              </label>
              <input
                type="datetime-local"
                value={unlockDate}
                onChange={(e) => setUnlockDate(e.target.value)}
                min={getTomorrowDate()}
                required
                className="w-full px-4 py-3 glass rounded-lg focus:outline-none focus:ring-2 focus:ring-capsule-gold transition-all"
              />
            </motion.div>

            {/* Description */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <label className="block text-sm font-medium mb-2">Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 glass rounded-lg focus:outline-none focus:ring-2 focus:ring-capsule-gold transition-all resize-none"
                placeholder="Add a description for your time capsule..."
              />
            </motion.div>

            {/* Submit Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex items-center space-x-4 pt-4"
            >
              <MagneticButton>
                <motion.button
                  type="submit"
                  disabled={loading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex-1 px-6 py-4 bg-gradient-to-r from-capsule-gold via-yellow-400 to-capsule-gold text-black font-bold rounded-xl hover:shadow-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 relative overflow-hidden group"
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
                      <span className="relative z-10">Create Capsule</span>
                    </>
                  )}
                </motion.button>
              </MagneticButton>

              <motion.button
                type="button"
                onClick={() => navigate('/dashboard')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-6 py-3 glass-strong rounded-lg hover:bg-white/20 transition-all"
              >
                Cancel
              </motion.button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

export default CreateCapsule

