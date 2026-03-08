import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, register as apiRegister, getProfile } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const login = async (credentials) => {
    const res = await apiLogin(credentials)
    if (res.data.code === 200) {
      token.value = res.data.data.token
      userInfo.value = res.data.data.user
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
    return res
  }

  const register = async (userData) => {
    return await apiRegister(userData)
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  const fetchProfile = async () => {
    const res = await getProfile()
    if (res.data.code === 200) {
      userInfo.value = res.data.data
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
  }

  return { token, userInfo, login, register, logout, fetchProfile }
})