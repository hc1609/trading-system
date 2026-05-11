import { defineStore } from 'pinia'
import axios from 'axios'

export const usePositionStore = defineStore('position', {
  state: () => ({
    positions: [],
    etfRecommendation: null,
    daytradeStatus: null,
    riskStatus: null,
    summary: null,
    loading: false
  }),
  
  getters: {
    holdingPositions: (state) => state.positions.filter(p => p.status === 'holding'),
    etfPositions: (state) => state.positions.filter(p => p.type === 'etf'),
    individualPositions: (state) => state.positions.filter(p => p.type === 'individual'),
    totalValue: (state) => state.summary?.total_value || 0
  },
  
  actions: {
    async fetchPositions() {
      this.loading = true
      try {
        const response = await axios.get('/api/position/positions/')
        this.positions = response.data.results || response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      } finally {
        this.loading = false
      }
    },
    
    async fetchSummary() {
      try {
        const response = await axios.get('/api/position/summary/')
        this.summary = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async fetchEtfRecommendation() {
      try {
        const response = await axios.get('/api/position/etf/recommendation/')
        this.etfRecommendation = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async fetchDaytradeStatus() {
      try {
        const response = await axios.get('/api/daytrade/status/')
        this.daytradeStatus = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async fetchRiskStatus() {
      try {
        const response = await axios.get('/api/risk/current/')
        this.riskStatus = response.data
        return { success: true }
      } catch (error) {
        return { success: false, error: error.message }
      }
    },
    
    async openPosition(positionData) {
      try {
        const response = await axios.post('/api/position/open/', positionData)
        await this.fetchPositions()
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '开仓失败' }
      }
    },
    
    async closePosition(positionId, sellData) {
      try {
        const response = await axios.post(`/api/position/${positionId}/close/`, sellData)
        await this.fetchPositions()
        return { success: true, data: response.data }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '平仓失败' }
      }
    },
    
    async refreshAll() {
      await Promise.all([
        this.fetchPositions(),
        this.fetchSummary(),
        this.fetchEtfRecommendation(),
        this.fetchDaytradeStatus(),
        this.fetchRiskStatus()
      ])
    }
  }
})
