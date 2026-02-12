import { createContext, useState, useContext, useEffect } from 'react'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token')
      const savedUser = localStorage.getItem('user')
      
      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser))
          setIsAuthenticated(true)
          // Verify token is still valid
          await authAPI.getProfile()
        } catch (error) {
          // Token invalid, clear storage
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setUser(null)
          setIsAuthenticated(false)
        }
      }
      setLoading(false)
    }
    
    initAuth()
  }, [])

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password })
      const { token, user: userData } = response.data
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
      setIsAuthenticated(true)
      
      toast.success('Welcome back!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || error.message || 'Login failed'
      console.error('Login error:', error.response?.data || message)
      throw { response: error.response, message: message }
    }
  }

  const register = async (email, password, displayName) => {
    try {
      console.log('Register request:', { email, display_name: displayName })
      const response = await authAPI.register({ email, password, display_name: displayName })
      const { token, user: userData } = response.data
      
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userData))
      setUser(userData)
      setIsAuthenticated(true)
      
      // Don't show toast here - let the component handle it
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Registration failed'
      console.error('Registration error:', error.response?.data || message)
      // Re-throw error so component can catch and handle it
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
    toast.success('Logged out successfully')
  }

  const updateUser = async (displayName) => {
    try {
      const response = await authAPI.updateProfile({ display_name: displayName })
      const updatedUser = response.data.user
      setUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
      toast.success('Profile updated!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Update failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

