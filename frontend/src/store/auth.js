import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    userProfile: (state) => state.user?.profile || {}
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/auth/login/', {
          username,
          password
        })
        
        this.token = response.data.access
        this.refreshToken = response.data.refresh
        this.user = response.data.user
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        
        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.error || '登录失败'
        }
      }
    },
    
    async register(username, password, email) {
      try {
        const response = await axios.post('/api/auth/register/', {
          username,
          password,
          email
        })
        
        this.token = response.data.access
        this.refreshToken = response.data.refresh
        this.user = response.data.user
        
        localStorage.setItem('token', this.token)
        localStorage.setItem('refreshToken', this.refreshToken)
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data || '注册失败'
        }
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      
      delete axios.defaults.headers.common['Authorization']
    },
    
    async fetchProfile() {
      try {
        const response = await axios.get('/api/auth/profile/')
        this.user = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: '获取用户信息失败' }
      }
    },
    
    async updateProfile(profileData) {
      try {
        const response = await axios.put('/api/auth/profile/', {
          profile: profileData
        })
        this.user = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: '更新配置失败' }
      }
    }
  }
})
