import api from './api'

export const login = async (username, password) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  const { access_token, refresh_token } = response.data
  localStorage.setItem('access_token', access_token)
  localStorage.setItem('refresh_token', refresh_token)

  // Get user info
  const userResponse = await api.get('/auth/me')
  const userData = userResponse.data
  
  // Extract roles from token
  try {
    const payload = JSON.parse(atob(access_token.split('.')[1]))
    userData.roles = payload.roles || []
  } catch (e) {
    userData.roles = []
  }
  
  return { ...response.data, user: userData }
}

export const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}
