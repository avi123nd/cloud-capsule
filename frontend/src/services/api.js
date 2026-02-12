import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if already on login page
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  deleteAccount: () => api.delete('/auth/delete'),
  refreshToken: () => api.post('/auth/refresh-token'),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
}

// Capsule API
export const capsuleAPI = {
  create: (formData) => api.post('/capsules', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getAll: (params) => api.get('/capsules', { params }),
  getById: (id) => api.get(`/capsules/${id}`),
  update: (id, formData) => {
    // Check if formData is FormData (file upload) or regular object
    if (formData instanceof FormData) {
      return api.put(`/capsules/${id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }
    return api.put(`/capsules/${id}`, formData)
  },
  delete: (id) => api.delete(`/capsules/${id}`),
  unlock: (id) => api.post(`/capsules/${id}/unlock`),
  getMetadata: (id) => api.get(`/capsules/${id}/metadata`),
  preview: (id) => api.get(`/capsules/${id}/preview`),
  previewEdit: (id) => api.get(`/capsules/${id}/preview-edit`),
  download: (id) => api.get(`/capsules/${id}/download`, { responseType: 'blob' }),
}

// Dashboard API
export const dashboardAPI = {
  getDashboard: (params) => api.get('/dashboard', { params }),
  getUnlocked: () => api.get('/dashboard/unlocked'),
  getUpcoming: () => api.get('/dashboard/upcoming'),
  getStats: () => api.get('/dashboard/stats'),
}

// Users API
export const usersAPI = {
  search: (q) => api.get('/users/search', { params: { q } }),
}

export default api

