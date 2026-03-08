import request from './request'

export const getTasks = (params) => request.get('/tasks/', { params })
export const createTask = (data) => request.post('/tasks/', data)
export const updateTask = (id, data) => request.put(`/tasks/${id}`, data)
export const deleteTask = (id) => request.delete(`/tasks/${id}`)
export const remindTasks = () => request.post('/tasks/remind')
export const testEmail = () => request.get('/tasks/test-email')