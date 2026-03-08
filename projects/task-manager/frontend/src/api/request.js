import axios from 'axios'

const request = axios.create({
  baseURL: '/api',            // 使用代理，所以直接写 /api
  timeout: 5000,
})

// 请求拦截器：自动添加 token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // token 失效，清除本地信息并跳转登录
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request