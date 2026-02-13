import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Upload, X, Calendar, FileText, Image, Video, Music, Download, Eye, File, Clock, FileType, Save, RotateCcw, Pencil } from 'lucide-react'
import MinimalNavbar from '../components/MinimalNavbar'
import { capsuleAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

// FileEyeFrame Component - Eye visibility toggle for file preview and editing
const FileEyeFrame = ({
  fileData,
  isExpanded,
  onToggle,
  canEdit,
  onReplaceFile,
  onUpdateMetadata,
  onAddAnnotation
}) => {
  // Initialize annotation from fileData
  const [localAnnotation, setLocalAnnotation] = useState(fileData?.annotation || '')
  const [isEditingAnnotation, setIsEditingAnnotation] = useState(false)
  
  // Update localAnnotation when fileData changes
  useEffect(() => {
    if (fileData?.annotation !== undefined) {
      setLocalAnnotation(fileData.annotation)
    }
  }, [fileData?.annotation])
  
  const formatDate = (dateString) => {
    if (!dateString || dateString === 'Not available') {
      return 'Just now'
    }
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return 'Just now'
      }
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Just now'
    }
  }

  const getFileExtension = (filename) => {
    if (!filename) return 'Unknown'
    return filename.split('.').pop()?.toLowerCase() || 'unknown'
  }

  const getFileSize = (bytes) => {
    // Handle undefined, null, or missing size
    if (bytes === undefined || bytes === null) {
      return 'Not available'
    }
    if (bytes === 0) {
      return '0 bytes'
    }
    if (bytes < 1024) return `${bytes} bytes`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`
  }

  const handleSaveAnnotation = () => {
    setLocalAnnotation(localAnnotation)
    setIsEditingAnnotation(false)
    if (onAddAnnotation) {
      onAddAnnotation(localAnnotation)
    }
  }

  const handleReplaceClick = () => {
    if (onReplaceFile) {
      onReplaceFile()
    }
  }

  if (!fileData) {
    return null
  }

  return (
    <div className="mt-4">
      {/* Eye Frame Toggle Button */}
      <motion.button
        type="button"
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          onToggle()
        }}
        className={`w-full flex items-center justify-between p-4 rounded-xl transition-all duration-300 ${
          isExpanded 
            ? 'bg-neutral-900 text-white' 
            : 'bg-neutral-100 hover:bg-neutral-200 text-neutral-700'
        }`}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <div className="flex items-center space-x-3">
          <Eye className={`w-5 h-5 ${isExpanded ? 'text-white' : 'text-neutral-500'}`} />
          <div className="text-left">
            <p className="font-medium">
              {fileData.name || fileData.filename || 'Uploaded File'}
            </p>
            <p className={`text-xs ${isExpanded ? 'text-neutral-400' : 'text-neutral-500'}`}>
              {isExpanded ? 'Tap to collapse' : 'Tap to view details'}
            </p>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <svg 
            className={`w-5 h-5 ${isExpanded ? 'text-white' : 'text-neutral-400'}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </motion.div>
      </motion.button>

      {/* Expanded File Details Panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: 'auto', marginTop: 12 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="bg-white border-2 border-neutral-200 rounded-xl p-6 shadow-lg">
              {/* File Header with Metadata */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center space-x-3 p-3 bg-neutral-50 rounded-lg">
                  <FileType className="w-5 h-5 text-neutral-500" />
                  <div>
                    <p className="text-xs text-neutral-500 uppercase tracking-wide">Format</p>
                    <p className="font-medium text-neutral-900">{getFileExtension(fileData.name || fileData.filename)}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-neutral-50 rounded-lg">
                  <Clock className="w-5 h-5 text-neutral-500" />
                  <div>
                    <p className="text-xs text-neutral-500 uppercase tracking-wide">Uploaded</p>
                    <p className="font-medium text-neutral-900">{formatDate(fileData.uploadDate || fileData.createdAt)}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-neutral-50 rounded-lg">
                  <FileText className="w-5 h-5 text-neutral-500" />
                  <div>
                    <p className="text-xs text-neutral-500 uppercase tracking-wide">Size</p>
                    <p className="font-medium text-neutral-900">{getFileSize(fileData.size)}</p>
                  </div>
                </div>
                {fileData.storageType && (
                  <div className="flex items-center space-x-3 p-3 bg-neutral-50 rounded-lg">
                    <div className={`w-3 h-3 rounded-full ${fileData.storageType === 'cloudinary' ? 'bg-blue-500' : 'bg-green-500'}`} />
                    <div>
                      <p className="text-xs text-neutral-500 uppercase tracking-wide">Storage</p>
                      <p className="font-medium text-neutral-900">{fileData.storageType === 'cloudinary' ? 'Cloudinary' : 'GridFS'}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* File Content Preview */}
              {fileData.previewUrl && (
                <div className="mb-6">
                  <p className="text-sm font-medium text-neutral-700 mb-3">Full File Preview</p>
                  <div className="relative rounded-xl overflow-hidden bg-neutral-100 border border-neutral-200">
                    {/* Image Preview - Check by type OR extension */}
                    {(fileData.type?.startsWith('image/') || 
                     (fileData.extension && ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileData.extension)) ||
                     (fileData.name?.match(/\.(jpg|jpeg|png|gif|webp)$/i))) ? (
                      <img 
                        src={fileData.previewUrl} 
                        alt={fileData.name || fileData.filename}
                        className="w-full max-h-[500px] object-contain"
                        style={{ minHeight: '200px', backgroundColor: '#f5f5f5' }}
                      />
                    ) : /* Video Preview */ (
                      (fileData.type?.startsWith('video/') || 
                       (fileData.extension && ['mp4', 'webm', 'mov', 'avi'].includes(fileData.extension)) ||
                       (fileData.name?.match(/\.(mp4|webm|mov|avi)$/i))) ? (
                        <video 
                          src={fileData.previewUrl}
                          controls
                          autoPlay={false}
                          className="w-full max-h-[500px]"
                          style={{ minHeight: '300px' }}
                        />
                      ) : /* Audio Preview */ (
                        (fileData.type?.startsWith('audio/') || 
                         (fileData.extension && ['mp3', 'wav', 'ogg', 'm4a'].includes(fileData.extension)) ||
                         (fileData.name?.match(/\.(mp3|wav|ogg|m4a)$/i))) ? (
                          <div className="p-6">
                            <div className="flex items-center justify-center mb-4">
                              <Music className="w-16 h-16 text-neutral-400" />
                            </div>
                            <audio 
                              src={fileData.previewUrl}
                              controls
                              className="w-full"
                            />
                          </div>
                        ) : /* Document Preview */ (
                          <div className="p-8 text-center">
                            <File className="w-16 h-16 mx-auto text-neutral-400 mb-3" />
                            <p className="text-neutral-600 mb-3">{fileData.name || fileData.filename}</p>
                            <a
                              href={fileData.previewUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              Open Document
                            </a>
                          </div>
                        )
                      )
                    )}
                  </div>
                </div>
              )}

              {/* Annotation Section */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-neutral-700">Annotation</p>
                  {canEdit && !isEditingAnnotation && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault()
                        setIsEditingAnnotation(true)
                      }}
                      className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <Pencil className="w-3 h-3" />
                      <span>Edit</span>
                    </button>
                  )}
                </div>
                {isEditingAnnotation ? (
                  <div className="space-y-2">
                    <textarea
                      value={localAnnotation}
                      onChange={(e) => setLocalAnnotation(e.target.value)}
                      placeholder="Add an annotation or note about this file..."
                      rows={3}
                      className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-neutral-900 focus:border-transparent resize-none"
                    />
                    <div className="flex justify-end space-x-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault()
                          setIsEditingAnnotation(false)
                          setLocalAnnotation(fileData.annotation || '')
                        }}
                        className="px-3 py-1 text-xs text-neutral-600 hover:text-neutral-900"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault()
                          handleSaveAnnotation()
                        }}
                        className="px-3 py-1 text-xs bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 flex items-center space-x-1"
                      >
                        <Save className="w-3 h-3" />
                        <span>Save</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-neutral-600 bg-neutral-50 p-3 rounded-lg min-h-[3rem]">
                    {localAnnotation || 'No annotation added yet'}
                  </p>
                )}
              </div>

              {/* Edit Actions */}
              {canEdit && (
                <div className="flex flex-wrap gap-3 pt-4 border-t border-neutral-200">
                  <motion.button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault()
                      handleReplaceClick()
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Replace File</span>
                  </motion.button>
                  {fileData.previewUrl && (
                    <motion.a
                      href={fileData.previewUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-sm transition-colors"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Eye className="w-4 h-4" />
                      <span>Full Preview</span>
                    </motion.a>
                  )}
                  <motion.button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault()
                      const url = fileData.previewUrl || fileData.cloudinaryUrl || fileData.storageUrl
                      if (url) {
                        const a = document.createElement('a')
                        a.href = url
                        a.download = fileData.name || fileData.filename
                        a.click()
                      }
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-50 hover:bg-green-100 text-green-700 rounded-lg text-sm transition-colors ml-auto"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </motion.button>
                </div>
              )}

              {/* Non-editable view notice */}
              {!canEdit && (
                <div className="flex items-center justify-center space-x-2 pt-4 border-t border-neutral-200 text-neutral-500 text-sm">
                  <Eye className="w-4 h-4" />
                  <span>View only - Contact the owner to make changes</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const UpdateCapsule = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [loadingCapsule, setLoadingCapsule] = useState(true)
  const [description, setDescription] = useState('')
  const [unlockDate, setUnlockDate] = useState('')
  const [file, setFile] = useState(null)
  const [filePreview, setFilePreview] = useState(null)
  const [capsule, setCapsule] = useState(null)
  const [currentImagePreview, setCurrentImagePreview] = useState(null)
  const [currentVideoPreview, setCurrentVideoPreview] = useState(null)
  const [currentAudioPreview, setCurrentAudioPreview] = useState(null)
  const [documentUrl, setDocumentUrl] = useState(null)
  const [expandedFileId, setExpandedFileId] = useState(null)
  const [editingField, setEditingField] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [annotation, setAnnotation] = useState('')
  const [updateSuccess, setUpdateSuccess] = useState(false)
  const [newFileType, setNewFileType] = useState(null)
  const [newFileSize, setNewFileSize] = useState(null)
  const fileInputRef = useRef(null)
  
  // Check if user can edit (is owner or authorized)
  const canEdit = capsule && user && (
    capsule.user_id === user.uid || 
    capsule.sender_id === user.uid ||
    capsule.authorized_editors?.includes(user.uid)
  )

  // Prepare file data for FileEyeFrame
  const getCurrentFileData = () => {
    if (!capsule) return null
    
    const fileUrl = capsule.cloudinary_url || capsule.storage_info?.url
    const extension = capsule.filename?.split('.').pop()?.toLowerCase() || ''
    
    // Determine preview URL based on file type
    let previewUrl = null
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
      previewUrl = fileUrl || currentImagePreview
    } else if (['mp4', 'webm', 'mov', 'avi'].includes(extension)) {
      previewUrl = fileUrl || currentVideoPreview
    } else if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension)) {
      previewUrl = fileUrl || currentAudioPreview
    } else if (['pdf', 'doc', 'docx', 'txt'].includes(extension)) {
      previewUrl = fileUrl || documentUrl
    }
    
    return {
      id: capsule._id || capsule.id,
      name: capsule.filename,
      filename: capsule.filename,
      type: capsule.file_type,
      extension: extension,
      size: capsule.file_size || 0,
      uploadDate: capsule.createdAt || capsule.upload_date,
      createdAt: capsule.createdAt,
      previewUrl: previewUrl,
      cloudinaryUrl: capsule.cloudinary_url,
      storageUrl: capsule.storage_info?.url,
      storageType: capsule.storage_type,
      annotation: capsule.annotation || ''
    }
  }

  const getNewFileData = () => {
    if (!file) return null
    
    const extension = file.name?.split('.').pop()?.toLowerCase() || ''
    
    return {
      id: 'new-file',
      name: file.name,
      filename: file.name,
      type: file.type || getMimeTypeFromExtension(extension),
      extension: extension,
      size: file.size || 0,
      uploadDate: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      previewUrl: filePreview,
      storageType: 'new',
      annotation: ''
    }
  }

  const getMimeTypeFromExtension = (extension) => {
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'webp': 'image/webp',
      'mp4': 'video/mp4',
      'webm': 'video/webm',
      'mov': 'video/quicktime',
      'avi': 'video/x-msvideo',
      'mp3': 'audio/mpeg',
      'wav': 'audio/wav',
      'ogg': 'audio/ogg',
      'm4a': 'audio/mp4',
      'pdf': 'application/pdf',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'txt': 'text/plain'
    }
    return mimeTypes[extension] || 'application/octet-stream'
  }

  const handleToggleFileExpand = (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setExpandedFileId(expandedFileId === 'current-file' ? null : 'current-file')
  }

  const handleToggleNewFileExpand = (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setExpandedFileId(expandedFileId === 'new-file' ? null : 'new-file')
  }

  const handleReplaceFile = (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleUpdateMetadata = (data) => {
    toast.success('Metadata update mode activated')
    if (data.name) {
      setEditValue(data.name)
      setEditingField('name')
    }
  }

  const handleAddAnnotation = (annotationText) => {
    setAnnotation(annotationText)
    toast.success('Annotation saved')
  }

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
    else if (extension === 'pdf') mimeType = 'application/pdf'
    
    const blob = new Blob([byteArray], { type: mimeType })
    return URL.createObjectURL(blob)
  }

  useEffect(() => {
    loadCapsule()
  }, [id])

  const loadCapsule = async () => {
    try {
      const response = await capsuleAPI.getById(id)
      const capsuleData = response.data
      setCapsule(capsuleData)
      setDescription(capsuleData.description || '')
      
      // Load file preview
      const fileUrl = capsuleData.cloudinary_url || capsuleData.storage_info?.url
      const extension = capsuleData.filename?.split('.').pop()?.toLowerCase() || ''
      
      if (fileUrl) {
        // Use direct URL for Cloudinary files
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
          setCurrentImagePreview(fileUrl)
        } else if (['mp4', 'webm', 'mov', 'avi'].includes(extension)) {
          setCurrentVideoPreview(fileUrl)
        } else if (['mp3', 'wav', 'ogg', 'm4a'].includes(extension)) {
          setCurrentAudioPreview(fileUrl)
        } else if (['pdf', 'doc', 'docx', 'txt'].includes(extension)) {
          setDocumentUrl(fileUrl)
        }
      } else if (capsuleData.capsule_type !== 'text' && user) {
        // No direct URL, try API for GridFS files (only for owners)
        const isOwner = capsuleData.user_id === user.uid || capsuleData.sender_id === user.uid
        if (isOwner) {
          try {
            const previewResponse = await capsuleAPI.previewEdit(id)
            if (previewResponse.data.data) {
              const url = createBlobUrlFromBase64(previewResponse.data.data, capsuleData.filename)
              const ext = capsuleData.filename?.split('.').pop()?.toLowerCase()
              
              if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
                setCurrentImagePreview(url)
              } else if (['mp4', 'webm', 'mov', 'avi'].includes(ext)) {
                setCurrentVideoPreview(url)
              } else if (['mp3', 'wav', 'ogg', 'm4a'].includes(ext)) {
                setCurrentAudioPreview(url)
              } else if (['pdf', 'doc', 'docx', 'txt'].includes(ext)) {
                setDocumentUrl(url)
              }
            }
          } catch (previewError) {
            console.error('Failed to load preview:', previewError)
          }
        }
      }
      
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
      setNewFileType(selectedFile.type || '')
      setNewFileSize(selectedFile.size || 0)
      
      // Get file extension for fallback detection
      const fileName = selectedFile.name || ''
      const extension = fileName.split('.').pop()?.toLowerCase() || ''
      
      const isImageType = selectedFile.type?.startsWith('image/') || 
        ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)
      const isVideoType = selectedFile.type?.startsWith('video/') || 
        ['mp4', 'webm', 'mov', 'avi'].includes(extension)
      const isAudioType = selectedFile.type?.startsWith('audio/') || 
        ['mp3', 'wav', 'ogg', 'm4a'].includes(extension)
      
      // Create preview based on file type
      if (isImageType) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setFilePreview(e.target.result)
        }
        reader.readAsDataURL(selectedFile)
      } else if (isVideoType) {
        // For videos, create a blob URL
        const videoUrl = URL.createObjectURL(selectedFile)
        setFilePreview(videoUrl)
      } else if (isAudioType) {
        // For audio, create a blob URL
        const audioUrl = URL.createObjectURL(selectedFile)
        setFilePreview(audioUrl)
      } else {
        setFilePreview(null)
      }
    }
  }

  const removeFile = () => {
    setFile(null)
    setFilePreview(null)
    setNewFileType(null)
    setNewFileSize(null)
    setCurrentImagePreview(null)
  }

  // Handle direct download using Cloudinary/storage URL
  const handleDownload = () => {
    const fileUrl = capsule?.cloudinary_url || capsule?.storage_info?.url
    if (!fileUrl) {
      toast.error('No file available for download')
      return
    }
    
    // Create a temporary anchor element for direct download
    const a = document.createElement('a')
    a.href = fileUrl
    a.download = capsule.filename
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    a.click()
    
    toast.success('Download started')
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

      toast.success('Capsule updated successfully!')
      setUpdateSuccess(true)
      
      // Reload the capsule data to show updated content
      await loadCapsule()
      
      // Reset expanded state to show previews
      setExpandedFileId('current-file')
      
      // Clear the file input since it was uploaded
      setFile(null)
      setFilePreview(null)
      setNewFileType(null)
      setNewFileSize(null)
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

  const getFileSize = (bytes) => {
    if (bytes === undefined || bytes === null || bytes === 0) {
      return 'Size unknown'
    }
    if (bytes < 1024) return `${bytes} bytes`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`
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
                <div className="space-y-4">
                  {/* File Card - Clear File Identification */}
                  <div className="bg-white border-2 border-neutral-200 rounded-xl p-6 shadow-sm">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-neutral-100 rounded-xl flex items-center justify-center">
                          {file.type?.startsWith('image/') || file.name?.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
                            <Image className="w-8 h-8 text-blue-500" />
                          ) : file.type?.startsWith('video/') || file.name?.match(/\.(mp4|webm|mov|avi)$/i) ? (
                            <Video className="w-8 h-8 text-purple-500" />
                          ) : file.type?.startsWith('audio/') || file.name?.match(/\.(mp3|wav|ogg|m4a)$/i) ? (
                            <Music className="w-8 h-8 text-green-500" />
                          ) : (
                            <File className="w-8 h-8 text-neutral-400" />
                          )}
                        </div>
                        <div>
                          <p className="font-semibold text-neutral-900 text-lg">{file.name}</p>
                          <p className="text-sm text-neutral-500">{file.name?.split('.').pop()?.toUpperCase() || 'FILE'} File</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={removeFile}
                        className="p-2 hover:bg-red-50 rounded-lg transition-colors text-red-500"
                        title="Remove file"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    
                    {/* File Details Grid */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-1">Size</p>
                        <p className="font-medium text-neutral-900">{getFileSize(file.size)}</p>
                      </div>
                      <div className="bg-neutral-50 rounded-lg p-3">
                        <p className="text-xs text-neutral-500 uppercase tracking-wide mb-1">Uploaded</p>
                        <p className="font-medium text-neutral-900">Just now</p>
                      </div>
                    </div>
                    
                    {/* Replace File Button - Clearly Visible */}
                    <label className="flex items-center justify-center w-full py-3 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg cursor-pointer transition-colors font-medium">
                      <RotateCcw className="w-5 h-5 mr-2" />
                      Replace File
                      <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleFileChange}
                        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                      />
                    </label>
                  </div>
                  
                  {/* Full New File Preview - Outside Eye Frame */}
                  {/* Image Preview - Check by type OR extension */}
                  {filePreview && (newFileType?.startsWith('image/') || 
                   file?.name?.match(/\.(jpg|jpeg|png|gif|webp)$/i)) && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-neutral-700 mb-2">Full Image Preview</p>
                      <img 
                        src={filePreview} 
                        alt="Preview" 
                        className="w-full max-h-[500px] object-contain rounded-xl border border-neutral-200"
                        style={{ minHeight: '200px', backgroundColor: '#f5f5f5' }}
                      />
                    </div>
                  )}
                  
                  {/* Video Preview */}
                  {filePreview && (newFileType?.startsWith('video/') || 
                   file?.name?.match(/\.(mp4|webm|mov|avi)$/i)) && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-neutral-700 mb-2">Full Video Preview</p>
                      <div className="relative rounded-xl overflow-hidden border border-neutral-200">
                        <video 
                          src={filePreview}
                          controls
                          autoPlay={false}
                          className="w-full max-h-[500px]"
                          style={{ minHeight: '300px' }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Audio Preview */}
                  {filePreview && (newFileType?.startsWith('audio/') || 
                   file?.name?.match(/\.(mp3|wav|ogg|m4a)$/i)) && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-neutral-700 mb-2">Full Audio Preview</p>
                      <div className="bg-neutral-100 rounded-xl p-6 border border-neutral-200">
                        <div className="flex items-center justify-center mb-4">
                          <Music className="w-16 h-16 text-neutral-400" />
                        </div>
                        <audio 
                          src={filePreview}
                          controls
                          className="w-full"
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Document Info */}
                  {file && !newFileType?.startsWith('image/') && !newFileType?.startsWith('video/') && !newFileType?.startsWith('audio/') && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-neutral-700 mb-2">File Information</p>
                      <div className="bg-neutral-100 rounded-xl p-6 border border-neutral-200">
                        <div className="flex items-center">
                          <File className="w-12 h-12 text-neutral-400 mr-3" />
                          <div>
                            <p className="font-medium text-neutral-900">{file.name}</p>
                            <p className="text-sm text-neutral-500">{getFileSize(file.size)}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : capsule?.cloudinary_url || capsule?.storage_info?.url ? (
                // Show current file from Cloudinary/GridFS with Eye Frame
                <div className="space-y-4">
                  <div className="luxury-card p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getFileIcon()}
                        <div>
                          <p className="text-xs text-green-600 flex items-center mt-1">
                            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                            File stored in {capsule.storage_type === 'cloudinary' ? 'Cloudinary' : 'GridFS'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {/* Eye Frame Toggle */}
                        <motion.button
                          type="button"
                          onClick={handleToggleFileExpand}
                          className={`p-2 rounded-lg transition-colors ${
                            expandedFileId === 'current-file'
                              ? 'bg-neutral-900 text-white'
                              : 'hover:bg-neutral-100 text-blue-600'
                          }`}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          title={expandedFileId === 'current-file' ? 'Collapse details' : 'View file details'}
                        >
                          <Eye className="w-5 h-5" />
                        </motion.button>
                        {/* Download button */}
                        <button
                          type="button"
                          onClick={handleDownload}
                          className="p-2 hover:bg-neutral-100 rounded-lg transition-colors text-green-600"
                          title="Download File"
                        >
                          <Download className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Change File Button */}
                    {canEdit && (
                      <label className="mt-3 inline-flex items-center px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg cursor-pointer transition-colors text-sm">
                        <Upload className="w-4 h-4 mr-2" />
                        Change File
                        <input
                          ref={fileInputRef}
                          type="file"
                          className="hidden"
                          onChange={handleFileChange}
                          accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                        />
                      </label>
                    )}
                  </div>
                  
                  {/* FileEyeFrame for current file */}
                  <FileEyeFrame
                    fileData={getCurrentFileData()}
                    isExpanded={expandedFileId === 'current-file'}
                    onToggle={handleToggleFileExpand}
                    canEdit={canEdit}
                    onReplaceFile={canEdit ? handleReplaceFile : undefined}
                    onUpdateMetadata={canEdit ? handleUpdateMetadata : undefined}
                    onAddAnnotation={canEdit ? handleAddAnnotation : undefined}
                  />
                  
                  {/* Full Current Image Preview - Always show if cloudinary_url exists and it's an image */}
                  {(capsule?.cloudinary_url && capsule?.filename?.match(/\.(jpg|jpeg|png|gif|webp)$/i)) && (
                    <div className="mt-4">
                      <div className="relative rounded-xl overflow-hidden border border-neutral-200">
                        <img 
                          src={capsule?.cloudinary_url} 
                          alt="Current capsule image" 
                          className="w-full max-h-[500px] object-contain"
                          style={{ minHeight: '200px', backgroundColor: '#f5f5f5' }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Full Current Video Preview */}
                  {(capsule?.cloudinary_url && capsule?.filename?.match(/\.(mp4|webm|mov|avi)$/i)) && (
                    <div className="mt-4">
                      <div className="relative rounded-xl overflow-hidden border border-neutral-200">
                        <video 
                          src={capsule?.cloudinary_url}
                          controls
                          autoPlay={false}
                          className="w-full max-h-[500px]"
                          style={{ minHeight: '300px' }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Full Current Audio Preview */}
                  {(capsule?.cloudinary_url && capsule?.filename?.match(/\.(mp3|wav|ogg|m4a)$/i)) && (
                    <div className="mt-4">
                      <div className="bg-neutral-100 rounded-xl p-6 border border-neutral-200">
                        <div className="flex items-center justify-center mb-4">
                          <Music className="w-16 h-16 text-neutral-400" />
                        </div>
                        <audio 
                          src={capsule?.cloudinary_url}
                          controls
                          className="w-full"
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Full Current Document Preview */}
                  {(capsule?.cloudinary_url && capsule?.filename?.match(/\.(pdf|doc|docx|txt)$/i)) && (
                    <div className="mt-4">
                      <div className="bg-neutral-100 rounded-xl p-6 border border-neutral-200">
                        <a
                          href={capsule?.cloudinary_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-center text-blue-600 hover:text-blue-800"
                        >
                          <File className="w-8 h-8 mr-2" />
                          <span className="text-sm">View Full Document</span>
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              ) : capsule?.filename ? (
                // Fallback for older capsules
                <div className="luxury-card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getFileIcon()}
                      <div>
                        <p className="text-xs text-neutral-500">
                          Current file stored in {capsule.storage_type || 'GridFS'}
                        </p>
                      </div>
                    </div>
                    <p className="text-xs text-neutral-400">No preview available</p>
                  </div>
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
              {updateSuccess ? (
                <>
                  <motion.button
                    type="button"
                    onClick={() => navigate(`/capsule/${id}`)}
                    className="flex-1 px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors flex items-center justify-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Eye className="w-5 h-5 mr-2" />
                    View Updated Capsule
                  </motion.button>
                  <motion.button
                    type="button"
                    onClick={() => setUpdateSuccess(false)}
                    className="flex-1 px-6 py-3 bg-white border border-neutral-300 text-neutral-700 rounded-xl font-medium hover:bg-neutral-50 transition-colors"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Continue Editing
                  </motion.button>
                </>
              ) : (
                <>
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
                </>
              )}
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
