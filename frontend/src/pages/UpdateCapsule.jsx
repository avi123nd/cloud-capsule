import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Upload, X, Calendar, FileText, Image, Video, Music } from 'lucide-react'
import MinimalNavbar from '../components/MinimalNavbar'
import { capsuleAPI, usersAPI } from '../services/api'
import toast from 'react-hot-toast'

const UpdateCapsule = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [loadingCapsule, setLoadingCapsule] = useState(true)
  const [description, setDescription] = useState('')
  const [unlockDate, setUnlockDate] = useState('')
  const [file, setFile] = useState(null)
  const [filePreview, setFilePreview] = useState(null)
  const [capsule, setCapsule] = useState(null)

  useEffect(() => {
    loadCapsule()
  }, [id])

  const loadCapsule = async () => {
    try {
      const response = await capsuleAPI.getById(id)
      const capsuleData = response.data
      setCapsule(capzsuleData)
      setDescription(capsuleData.description || '')
      // Format unlock_date for datetime-local input
      if (capsuleData.unlock_date) {
        const date = new Date(capsuleData.unlock_date)
        const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
        setUnlockDate(localDate.toISOString().slice(0, 16))
      }
    } catch (error) {
      toast.error('Failed to load capsule')
      navigate('/dashboard')
    } finally {
      setLoadingCapsule(false)
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      
      // Create preview
      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => setFilePreview(e.target.result)
        reader.readAsDataURL(selectedFile)
      } else {
        setFilePreview(null)
      }
    }
  }

  const removeFile = () => {
    setFile(null)
    setFilePreview(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate that at least file or description is provided
    if (!file && !description.trim()) {
      toast.error('Please provide either a file or a description')
      return
    }
    
    if (!unlockDate) {
      toast.error('Please select an unlock date')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      
      // Add file only if provided
      if (file) {
        formData.append('file', file)
      }
      
      formData.append('unlock_date', unlockDate)
      
      // Add description if provided
      if (description.trim()) {
        formData.append('description', description.trim())
      }

      await capsuleAPI.update(id, formData)

      toast.success('Capsule updated successfully')
      navigate(`/capsule/${id}`)
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update capsule')
    } finally {
      setLoading(false)
    }
  }

  const getFileIcon = () => {
    if (!file && !capsule) return null
    const filename = file?.name || capsule?.filename || ''
    const extension = filename.split('.').pop()?.toLowerCase()
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
      return <Image className="w-5 h-5" />
    } else if (['mp4', 'webm', 'mov', 'avi'].includes(extension)) {
      return <Video className="w-5 h-5" />
    } else if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension)) {
      return <Music className="w-5 h-5" />
    }
    return <FileText className="w-5 h-5" />
  }

  if (loadingCapsule) {
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

      <div className="max-w-2xl mx-auto px-6 lg:px-8 py-12">
        <motion.button
          onClick={() => navigate(`/capsule/${id}`)}
          className="flex items-center space-x-2 text-neutral-600 hover:text-neutral-900 mb-8 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Capsule</span>
        </motion.button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="luxury-card p-8"
        >
          <h1 className="text-3xl font-semibold text-neutral-900 mb-2">Update Capsule</h1>
          <p className="text-neutral-600 mb-8">Modify your time capsule before it unlocks</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Message / Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Write a message or description for your capsule..."
                rows={4}
                className="luxury-input w-full resize-none"
              />
              <p className="mt-1 text-xs text-neutral-500">
                {!file && !description.trim() && 'Either a file or description is required'}
              </p>
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                File (Optional - leave empty to keep current file)
              </label>
              {file ? (
                <div className="luxury-card p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getFileIcon()}
                    <div>
                      <p className="font-medium text-neutral-900">{file.name}</p>
                      <p className="text-xs text-neutral-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={removeFile}
                    className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-neutral-600" />
                  </button>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-neutral-300 rounded-xl cursor-pointer hover:border-neutral-400 transition-colors luxury-card">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-8 h-8 mb-2 text-neutral-400" />
                    <p className="mb-2 text-sm text-neutral-600">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-neutral-500">
                      Images, Videos, Audio, Documents (Max 50MB)
                    </p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                  />
                </label>
              )}
              {filePreview && (
                <div className="mt-4 rounded-xl overflow-hidden">
                  <img src={filePreview} alt="Preview" className="w-full h-64 object-cover" />
                </div>
              )}
              {capsule?.filename && !file && (
                <p className="mt-2 text-xs text-neutral-500">
                  Current file: {capsule.filename}
                </p>
              )}
            </div>

            {/* Unlock Date */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Unlock Date & Time
              </label>
              <input
                type="datetime-local"
                value={unlockDate}
                onChange={(e) => setUnlockDate(e.target.value)}
                min={getTomorrowDate()}
                required
                className="luxury-input w-full"
              />
              <p className="mt-1 text-xs text-neutral-500">
                Select when this capsule should be unlocked
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4 pt-4">
              <button
                type="button"
                onClick={() => navigate(`/capsule/${id}`)}
                className="flex-1 px-6 py-3 bg-white border border-neutral-300 text-neutral-700 rounded-xl font-medium hover:bg-neutral-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || (!file && !description.trim() && !capsule?.filename)}
                className="flex-1 luxury-button disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Updating...' : 'Update Capsule'}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

function getTomorrowDate() {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().slice(0, 16)
}

export default UpdateCapsule
