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
      
      // The response data is already a blob when responseType: 'blob' is set
      let blob = response.data
      
      // If response.data is not a Blob, create one (fallback)
      if (!(blob instanceof Blob)) {
        const contentType = response.headers['content-type'] || 'application/octet-stream'
        blob = new Blob([response.data], { type: contentType })
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      
      // Extract filename from Content-Disposition header or use capsule filename
      const contentDisposition = response.headers['content-disposition']
      let filename = capsule.filename
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+?)"?(;|$)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1]
        }
      }
      
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Download started')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Failed to download file')
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
        <p className="text-neutral-600">Loading capsule...</p>
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
  const isOwner = user && capsule.user_id === user.uid

  return (
    <div className="min-h-screen bg-neutral-50">
      <Navbar />

      <div className="max-w-2xl mx-auto px-6 lg:px-8 py-12">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center space-x-2 text-neutral-600 hover:text-neutral-900 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="luxury-card p-8">
          {/* Title and Status */}
          <div className="mb-6">
            <h1 className="text-3xl font-semibold text-neutral-900 mb-2">{capsule.filename}</h1>
            <div className="flex items-center space-x-3">
              {isUnlocked ? (
                <span className="inline-flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                  <Unlock className="w-4 h-4" />
                  <span>Unlocked</span>
                </span>
              ) : (
                <span className="inline-flex items-center space-x-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                  <Lock className="w-4 h-4" />
                  <span>Locked</span>
                </span>
              )}
            </div>
          </div>

          {/* Info */}
          <div className="space-y-4 mb-6 pb-6 border-b border-neutral-200">
            {!isOwner && capsule.sender_name && (
              <div>
                <p className="text-sm text-neutral-600 mb-1">From</p>
                <p className="text-neutral-900 font-medium">{capsule.sender_name}</p>
                {capsule.sender_email && (
                  <p className="text-neutral-500 text-sm">{capsule.sender_email}</p>
                )}
              </div>
            )}
            {isOwner && (capsule.recipient_name || capsule.recipient_email || capsule.recipient_id) && (
              <div>
                <p className="text-sm text-neutral-600 mb-1">To</p>
                {capsule.recipient_name && (
                  <p className="text-neutral-900 font-medium">{capsule.recipient_name}</p>
                )}
                {capsule.recipient_display_email && (
                  <p className="text-neutral-500 text-sm">{capsule.recipient_display_email}</p>
                )}
                {capsule.recipient_email && !capsule.recipient_display_email && (
                  <p className="text-neutral-500 text-sm">{capsule.recipient_email}</p>
                )}
              </div>
            )}
            <div>
              <p className="text-sm text-neutral-600 mb-1">Unlock Date</p>
              <p className="text-neutral-900">{format(unlockDate, 'MMM dd, yyyy HH:mm')}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-600 mb-1">Created</p>
              <p className="text-neutral-900">{format(new Date(capsule.created_at), 'MMM dd, yyyy')}</p>
            </div>
            {isOwner && capsule.is_unlocked && capsule.unlocked_at && (
              <div>
                <p className="text-sm text-neutral-600 mb-1">Opened by Recipient</p>
                <p className="text-neutral-900 font-medium">{format(new Date(capsule.unlocked_at), 'MMM dd, yyyy HH:mm')}</p>
              </div>
            )}
            {capsule.description && (
              <div>
                <p className="text-sm text-neutral-600 mb-1">Description</p>
                <p className="text-neutral-900">{capsule.description}</p>
              </div>
            )}
          </div>

          {/* Preview */}
          {fileUrl && (
            <div className="mb-6 pb-6 border-b border-neutral-200">
              <p className="text-sm font-medium text-neutral-600 mb-3">Preview</p>
              {capsule.capsule_type === 'image' && (
                <img
                  src={fileUrl}
                  alt={capsule.filename}
                  className="w-full h-auto max-h-64 object-contain rounded-lg bg-neutral-100"
                  onError={() => toast.error('Failed to display image')}
                />
              )}
              {capsule.capsule_type === 'video' && (
                <video
                  src={fileUrl}
                  controls
                  className="w-full h-auto max-h-64 bg-neutral-100 rounded-lg"
                  onError={() => toast.error('Failed to display video')}
                />
              )}
              {capsule.capsule_type === 'audio' && (
                <audio src={fileUrl} controls className="w-full" />
              )}
            </div>
          )}

          {/* Time Remaining */}
          {!isUnlocked && (
            <div className="mb-6 pb-6 border-b border-neutral-200">
              <p className="text-sm text-neutral-600 mb-2">Time Remaining</p>
              <p className="text-lg font-semibold text-neutral-900">
                {now < unlockDate
                  ? `${daysUntil > 0 ? `${daysUntil} days` : `${hoursUntil} hours`}`
                  : 'Ready to unlock!'}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            {isUnlocked && (
              <button
                onClick={handleDownload}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
            )}
            {!isUnlocked && isOwner && (
              <button
                onClick={() => navigate(`/capsule/${id}/update`)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
            )}
            {canUnlock && !isOwner && (
              <button
                onClick={handleUnlock}
                disabled={unlocking}
                className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {unlocking ? 'Unlocking...' : 'Unlock'}
              </button>
            )}
            {isOwner && (
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CapsuleDetail
