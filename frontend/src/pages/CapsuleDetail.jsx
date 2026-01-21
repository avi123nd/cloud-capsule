import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Lock, Unlock, Calendar, Download, Edit, Trash2, Clock } from 'lucide-react'
import { format, differenceInDays, differenceInHours } from 'date-fns'
import Navbar from '../components/Navbar'
import { capsuleAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const CapsuleDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [capsule, setCapsule] = useState(null)
  const [loading, setLoading] = useState(true)
  const [unlocking, setUnlocking] = useState(false)
  const [fileUrl, setFileUrl] = useState(null)

  useEffect(() => {
    loadCapsule()
    // Cleanup blob URL on unmount
    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl)
      }
    }
  }, [id])
  
  // Helper function to create blob URL from base64 data
  const createBlobUrlFromBase64 = (base64Data, filename) => {
    const byteCharacters = atob(base64Data)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    
    const extension = filename.split('.').pop()?.toLowerCase() || ''
    let mimeType = 'application/octet-stream'
    
    if (['jpg', 'jpeg'].includes(extension)) mimeType = 'image/jpeg'
    else if (extension === 'png') mimeType = 'image/png'
    else if (extension === 'gif') mimeType = 'image/gif'
    else if (extension === 'mp4') mimeType = 'video/mp4'
    else if (extension === 'webm') mimeType = 'video/webm'
    else if (extension === 'mov') mimeType = 'video/quicktime'
    else if (extension === 'mp3') mimeType = 'audio/mpeg'
    else if (extension === 'wav') mimeType = 'audio/wav'
    else if (extension === 'ogg') mimeType = 'audio/ogg'
    else if (extension === 'm4a') mimeType = 'audio/mp4'
    
    const blob = new Blob([byteArray], { type: mimeType })
    return URL.createObjectURL(blob)
  }

  // Note: File preview loading is now handled in loadCapsule() to support locked capsule preview for senders

  const loadCapsule = async () => {
    try {
      const response = await capsuleAPI.getMetadata(id)
      const capsuleData = response.data
      setCapsule(capsuleData)
      
      // Load file preview if it's an image/video/audio
      // Allow sender to view locked capsules for editing, or show if unlocked
      if (capsuleData.capsule_type !== 'text' && !fileUrl) {
        const isSender = user && (capsuleData.user_id === user.uid || capsuleData.sender_id === user.uid)
        
        if (isSender || capsuleData.is_unlocked) {
          try {
            // Try preview endpoint first (works for locked capsules if sender)
            const previewResponse = await capsuleAPI.preview(id)
            if (previewResponse.data.data) {
              const url = createBlobUrlFromBase64(previewResponse.data.data, capsuleData.filename)
              setFileUrl(url)
            }
          } catch (previewError) {
            // If preview fails and capsule is unlocked, try unlock endpoint
            if (capsuleData.is_unlocked) {
              try {
                const unlockResponse = await capsuleAPI.unlock(id)
                if (unlockResponse.data.data) {
                  const url = createBlobUrlFromBase64(unlockResponse.data.data, capsuleData.filename)
                  setFileUrl(url)
                }
              } catch (unlockError) {
                console.error('Failed to load file:', unlockError)
              }
            }
          }
        }
      }
    } catch (error) {
      toast.error('Failed to load capsule')
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleUnlock = async () => {
    if (!confirm('Are you sure you want to unlock this capsule now?')) return

    setUnlocking(true)
    try {
      const response = await capsuleAPI.unlock(id)
      toast.success('Capsule unlocked!')
      
      // Create preview URL for images/videos/audio
      if (response.data.data && response.data.capsule_type !== 'text') {
        const filename = response.data.filename || capsule?.filename || ''
        const url = createBlobUrlFromBase64(response.data.data, filename)
        setFileUrl(url)
      }
      
      loadCapsule()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to unlock capsule')
    } finally {
      setUnlocking(false)
    }
  }

  const handleDownload = async () => {
    try {
      const response = await capsuleAPI.download(id)
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = capsule.filename
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Download started')
    } catch (error) {
      toast.error('Failed to download')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this capsule? This cannot be undone.')) return

    try {
      await capsuleAPI.delete(id)
      toast.success('Capsule deleted')
      navigate('/dashboard')
    } catch (error) {
      toast.error('Failed to delete capsule')
    }
  }

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

  if (!capsule) return null

  const unlockDate = new Date(capsule.unlock_date)
  const now = new Date()
  const isUnlocked = capsule.is_unlocked
  const canUnlock = now >= unlockDate && !isUnlocked
  const daysUntil = differenceInDays(unlockDate, now)
  const hoursUntil = differenceInHours(unlockDate, now)

  return (
    <div className="min-h-screen">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link to="/dashboard">
          <motion.button
            whileHover={{ x: -5 }}
            className="flex items-center space-x-2 mb-6 glass rounded-lg px-4 py-2 hover:bg-white/10 transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </motion.button>
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-strong rounded-2xl p-8"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gradient mb-2">{capsule.filename}</h1>
              {capsule.description && (
                <p className="text-gray-300">{capsule.description}</p>
              )}
            </div>
            {isUnlocked ? (
              <span className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg flex items-center space-x-2">
                <Unlock className="w-5 h-5" />
                <span>Unlocked</span>
              </span>
            ) : (
              <span className="px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg flex items-center space-x-2">
                <Lock className="w-5 h-5" />
                <span>Locked</span>
              </span>
            )}
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="glass rounded-lg p-4">
              <div className="flex items-center space-x-2 text-gray-400 mb-2">
                <Calendar className="w-4 h-4" />
                <span className="text-sm">Unlock Date</span>
              </div>
              <p className="font-medium">{format(unlockDate, 'MMM dd, yyyy HH:mm')}</p>
            </div>

            <div className="glass rounded-lg p-4">
              <div className="flex items-center space-x-2 text-gray-400 mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Created</span>
              </div>
              <p className="font-medium">{format(new Date(capsule.created_at), 'MMM dd, yyyy')}</p>
            </div>
          </div>

          {/* File Preview - Show when unlocked or for sender (for editing) */}
          {fileUrl && (
            <div className="glass rounded-lg p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-200">Preview</h3>
              {fileUrl ? (
                <>
                  {capsule.capsule_type === 'image' && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="rounded-xl overflow-hidden"
                    >
                      <img
                        src={fileUrl}
                        alt={capsule.filename}
                        className="w-full h-auto max-h-96 object-contain bg-black/20 rounded-lg"
                        onError={(e) => {
                          console.error('Image failed to load:', e)
                          toast.error('Failed to display image')
                        }}
                      />
                    </motion.div>
                  )}
                  {capsule.capsule_type === 'video' && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="rounded-xl overflow-hidden"
                    >
                      <video
                        src={fileUrl}
                        controls
                        className="w-full h-auto max-h-96 bg-black/20 rounded-lg"
                        onError={(e) => {
                          console.error('Video failed to load:', e)
                          toast.error('Failed to display video')
                        }}
                      >
                        Your browser does not support the video tag.
                      </video>
                    </motion.div>
                  )}
                  {capsule.capsule_type === 'audio' && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="rounded-xl overflow-hidden bg-black/20 p-6"
                    >
                      <audio src={fileUrl} controls className="w-full">
                        Your browser does not support the audio tag.
                      </audio>
                    </motion.div>
                  )}
                  {capsule.capsule_type === 'text' && (
                    <div className="rounded-xl bg-black/20 p-6">
                      <p className="text-gray-300 whitespace-pre-wrap">{capsule.description || 'No text content'}</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="w-16 h-16 border-4 border-gray-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-400">Loading preview...</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Status */}
          {!isUnlocked && (
            <div className="glass rounded-lg p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 mb-1">Time Remaining</p>
                  {now < unlockDate ? (
                    <p className="text-2xl font-bold text-capsule-gold">
                      {daysUntil > 0 ? `${daysUntil} days` : `${hoursUntil} hours`}
                    </p>
                  ) : (
                    <p className="text-2xl font-bold text-green-400">Ready to unlock!</p>
                  )}
                </div>
                {canUnlock && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleUnlock}
                    disabled={unlocking}
                    className="px-6 py-3 bg-gradient-to-r from-capsule-gold to-yellow-500 text-black font-bold rounded-lg hover:shadow-lg hover:shadow-capsule-gold/50 transition-all disabled:opacity-50"
                  >
                    {unlocking ? 'Unlocking...' : 'Unlock Now'}
                  </motion.button>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center space-x-4 pt-6 border-t border-white/10">
            {isUnlocked && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownload}
                className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 font-bold rounded-lg hover:shadow-lg transition-all"
              >
                <Download className="w-5 h-5" />
                <span>Download File</span>
              </motion.button>
            )}
            {!isUnlocked && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate(`/capsule/${id}/update`)}
                className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 font-bold rounded-lg hover:shadow-lg transition-all"
              >
                <Edit className="w-5 h-5" />
                <span>Edit Capsule</span>
              </motion.button>
            )}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleDelete}
              className="px-6 py-3 glass-strong rounded-lg hover:bg-red-500/20 transition-all flex items-center space-x-2"
            >
              <Trash2 className="w-5 h-5 text-red-400" />
              <span className="text-red-400">Delete</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default CapsuleDetail

