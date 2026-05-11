import { defineStore } from 'pinia'
import axios from 'axios'

export const useMarketStore = defineStore('market', {
  state: () => ({
    currentMarketState: null,
    latestMarketData: null,
    activeEvents: [],
    loading: false
  }),
  
  getters: {
    finalState: (state) => state.currentMarketState?.final_state || '未知',
    maxPosition: (state) => state.currentMarketState?.max_position || 0,
    etfAction: (state) => state.currentMarketState?.etf_action || '',
    individualAction: (state) => state.currentMarketState?.individual_action || ''
  },
  
  actions: {
    async fetchCurrentState() {
      this.loading = true
      try {
        const response = await axios.get('/api/strategy/current/')
        this.currentMarketState = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },
    
    async fetchLatestData() {
      try {
        const response = await axios.get('/api/market/latest/')
        this.latestMarketData = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async fetchActiveEvents() {
      try {
        const response = await axios.get('/api/strategy/events/active/')
        this.activeEvents = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async calculateState() {
      this.loading = true
      try {
        const response = await axios.post('/api/strategy/calculate/')
        this.currentMarketState = response.data.data
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '计算失败' }
      } finally {
        this.loading = false
      }
    },
    
    async refreshAll() {
      await Promise.all([
        this.fetchCurrentState(),
        this.fetchLatestData(),
        this.fetchActiveEvents()
      ])
    }
  }
})
