import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Upload, Calendar, FileText, X, ArrowLeft } from 'lucide-react'
import { format } from 'date-fns'
import MinimalNavbar from '../components/MinimalNavbar'
import { capsuleAPI, usersAPI } from '../services/api'
import toast from 'react-hot-toast'

const MinimalCreateCapsule = () => {
  const [file, setFile] = useState(null)
  const [unlockDate, setUnlockDate] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [recipientQuery, setRecipientQuery] = useState('')
  const [recipientOptions, setRecipientOptions] = useState([])
  const [recipient, setRecipient] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const navigate = useNavigate()

  const isEmail = (value) => {
    if (!value) return false
    return /\S+@\S+\.\S+/.test(value.trim())
  }

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
    
    const trimmedQuery = recipientQuery.trim()
    const hasSelectedRecipient = !!(recipient && recipient.uid)
    const hasExternalEmail = isEmail(trimmedQuery)

    // Validate recipient is required (either an existing user OR a raw email address)
    if (!hasSelectedRecipient && !hasExternalEmail) {
      toast.error('Please select a recipient or enter a valid email. Send To is mandatory.')
      return
    }
    
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
      
      if (recipient?.uid) {
        // Registered user
        formData.append('recipient_id', recipient.uid)
      } else if (hasExternalEmail) {
        // Non-registered email recipient
        formData.append('recipient_email', trimmedQuery)
      }

      const response = await capsuleAPI.create(formData)
      const capsuleId = response.data.capsule_id

      toast.success(
        (t) => (
          <div className="flex items-center justify-between">
            <span>Time capsule created successfully!</span>
            <button
              onClick={() => {
                toast.dismiss(t.id)
                navigate(`/capsule/${capsuleId}/update`)
              }}
              className="ml-4 px-3 py-1 text-xs font-medium bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
            >
              Edit
            </button>
          </div>
        ),
        { duration: 5000 }
      )
      // Navigate after a short delay to show the toast
      setTimeout(() => navigate('/dashboard'), 100)
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create capsule')
    } finally {
      setLoading(false)
    }
  }

  const onSearchRecipient = async (value) => {
    setRecipientQuery(value)
    setRecipient(null)
    if (!value || value.trim().length < 2) {
      setRecipientOptions([])
      return
    }
    try {
      const { data } = await usersAPI.search(value.trim())
      setRecipientOptions(data.users || [])
    } catch (e) {
      setRecipientOptions([])
    }
  }

  const getTomorrowDate = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().slice(0, 16)
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <MinimalNavbar />

      <div className="max-w-4xl mx-auto px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center space-x-2 text-neutral-600 hover:text-neutral-900 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </button>
          <h1 className="text-4xl font-semibold text-neutral-900 mb-2 tracking-tight">
            Create New Capsule
          </h1>
          <p className="text-neutral-600 text-lg">
            Preserve a memory for the future
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="luxury-card p-8"
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Recipient (required) */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                Send To <span className="text-red-500">*</span>
                <span className="text-neutral-500 text-xs font-normal ml-2">(Required)</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={recipient ? `${recipient.display_name || recipient.email}` : recipientQuery}
                  onChange={(e) => onSearchRecipient(e.target.value)}
                  placeholder="Search by name or email (required)"
                  className="luxury-input"
                  required
                />
                {recipientOptions.length > 0 && !recipient && (
                  <div className="absolute z-20 mt-2 w-full bg-white border border-neutral-200 rounded-xl shadow-lg max-h-56 overflow-auto">
                    {recipientOptions.map((u) => (
                      <button
                        key={u.uid}
                        type="button"
                        onClick={() => {
                          setRecipient(u)
                          setRecipientOptions([])
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-neutral-50"
                      >
                        <div className="text-neutral-900 font-medium">{u.display_name || u.email}</div>
                        {u.display_name && (
                          <div className="text-neutral-500 text-sm">{u.email}</div>
                        )}
                      </button>
                    ))}
                  </div>
                )}
                {recipient && (
                  <div className="mt-2 text-sm text-neutral-600">
                    Selected: <span className="font-medium text-neutral-900">{recipient.display_name || recipient.email}</span>
                    <button
                      type="button"
                      onClick={() => { setRecipient(null); setRecipientQuery('') }}
                      className="ml-3 text-neutral-500 hover:text-neutral-800 underline"
                    >
                      Clear
                    </button>
                  </div>
                )}
              </div>
            </div>
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                File (Optional)
              </label>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                  dragActive
                    ? 'border-neutral-900 bg-neutral-50'
                    : 'border-neutral-200 hover:border-neutral-300'
                }`}
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                  accept=".txt,.pdf,.png,.jpg,.jpeg,.gif,.mp4,.avi,.mov,.mp3,.wav,.ogg,.m4a,.aac,.flac"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  {file ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-center space-x-3">
                        <FileText className="w-8 h-8 text-neutral-900" />
                        <span className="font-medium text-neutral-900">{file.name}</span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            setFile(null)
                          }}
                          className="ml-2 text-neutral-400 hover:text-neutral-600 transition-colors"
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                      <p className="text-sm text-neutral-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="inline-block"
                      >
                        <Upload className="w-12 h-12 text-neutral-400 mx-auto" />
                      </motion.div>
                      <div>
                        <p className="text-neutral-700 font-medium mb-1">
                          Drag and drop your file here
                        </p>
                        <p className="text-sm text-neutral-500">
                          or <span className="text-neutral-900 underline">click to browse</span>
                        </p>
                        <p className="text-xs text-neutral-400 mt-3">
                          Supports: txt, pdf, images, videos, audio (mp3, wav, etc.) (Max 100MB)
                        </p>
                      </div>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Unlock Date */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3 flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>Unlock Date</span>
              </label>
              <input
                type="datetime-local"
                value={unlockDate}
                onChange={(e) => setUnlockDate(e.target.value)}
                min={getTomorrowDate()}
                required
                className="luxury-input"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                Description {!file && <span className="text-red-500">*</span>}
                {!file && <span className="text-neutral-500 text-xs font-normal ml-2">(Required if no file)</span>}
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="luxury-input resize-none"
                placeholder={file ? "Add a note about this memory..." : "Write your message or memory here..."}
              />
            </div>

            {/* Submit Button */}
            <div className="flex items-center space-x-4 pt-4">
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: loading ? 1 : 1.01 }}
                whileTap={{ scale: 0.99 }}
                className="luxury-button flex-1"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                    />
                    Creating...
                  </span>
                ) : (
                  'Create Capsule'
                )}
              </motion.button>

              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="luxury-button-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

export default MinimalCreateCapsule



