import axios from 'axios'
import type {
  AuthTokens,
  LoginCredentials,
  Candidate,
  CandidateListResponse,
  Application,
  JoiningNotice,
  Employee,
  DashboardStats,
  RecentActivity,
  User,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, null, {
            params: { token: refreshToken },
          })

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// ============================================
// AUTH
// ============================================

export const auth = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const { data } = await api.post('/auth/login', credentials)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data
  },

  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout')
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  },

  getMe: async (): Promise<User> => {
    const { data } = await api.get('/auth/me')
    return data
  },
}

// ============================================
// CANDIDATES
// ============================================

export const candidates = {
  list: async (params?: {
    page?: number
    page_size?: number
    status?: string
    search?: string
  }): Promise<CandidateListResponse> => {
    const { data } = await api.get('/candidates', { params })
    return data
  },

  get: async (id: number): Promise<Candidate> => {
    const { data } = await api.get(`/candidates/${id}`)
    return data
  },

  create: async (candidate: Partial<Candidate>): Promise<Candidate> => {
    const { data } = await api.post('/candidates', candidate)
    return data
  },

  update: async (id: number, candidate: Partial<Candidate>): Promise<Candidate> => {
    const { data } = await api.put(`/candidates/${id}`, candidate)
    return data
  },

  uploadDocument: async (
    id: number,
    file: File,
    documentType: string
  ): Promise<{ id: number; file_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(
      `/candidates/${id}/documents?document_type=${documentType}`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data
  },
}

// ============================================
// APPLICATIONS
// ============================================

export const applications = {
  list: async (params?: {
    status?: string
    candidate_id?: number
  }): Promise<Application[]> => {
    const { data } = await api.get('/applications', { params })
    return data
  },

  get: async (id: number): Promise<Application> => {
    const { data } = await api.get(`/applications/${id}`)
    return data
  },

  create: async (application: Partial<Application>): Promise<Application> => {
    const { data } = await api.post('/applications', application)
    return data
  },

  recordResult: async (
    id: number,
    result: { status: string; result_notes?: string }
  ): Promise<Application> => {
    const { data } = await api.put(`/applications/${id}/result`, result)
    return data
  },
}

// ============================================
// JOINING NOTICES
// ============================================

export const joiningNotices = {
  list: async (params?: { status?: string }): Promise<JoiningNotice[]> => {
    const { data } = await api.get('/joining-notices', { params })
    return data
  },

  get: async (id: number): Promise<JoiningNotice> => {
    const { data } = await api.get(`/joining-notices/${id}`)
    return data
  },

  create: async (notice: Partial<JoiningNotice>): Promise<JoiningNotice> => {
    const { data } = await api.post('/joining-notices', notice)
    return data
  },

  update: async (id: number, notice: Partial<JoiningNotice>): Promise<JoiningNotice> => {
    const { data } = await api.put(`/joining-notices/${id}`, notice)
    return data
  },

  submit: async (id: number): Promise<JoiningNotice> => {
    const { data } = await api.post(`/joining-notices/${id}/submit`)
    return data
  },

  approve: async (id: number): Promise<JoiningNotice> => {
    const { data } = await api.post(`/joining-notices/${id}/approve`)
    return data
  },

  reject: async (id: number, reason: string): Promise<JoiningNotice> => {
    const { data } = await api.post(`/joining-notices/${id}/reject`, { reason })
    return data
  },
}

// ============================================
// EMPLOYEES
// ============================================

export const employees = {
  list: async (params?: {
    employment_type?: string
    status?: string
    search?: string
    page?: number
    page_size?: number
  }): Promise<Employee[]> => {
    const { data } = await api.get('/employees', { params })
    return data
  },

  get: async (id: number): Promise<Employee> => {
    const { data } = await api.get(`/employees/${id}`)
    return data
  },

  update: async (id: number, employee: Partial<Employee>): Promise<Employee> => {
    const { data } = await api.put(`/employees/${id}`, employee)
    return data
  },

  terminate: async (id: number, terminationDate: string): Promise<Employee> => {
    const { data } = await api.post(
      `/employees/${id}/terminate?termination_date=${terminationDate}`
    )
    return data
  },

  getHaken: async (): Promise<Employee[]> => {
    const { data } = await api.get('/employees/haken')
    return data
  },

  getUkeoi: async (): Promise<Employee[]> => {
    const { data } = await api.get('/employees/ukeoi')
    return data
  },

  getStats: async (): Promise<{ total_active: number; haken_count: number; ukeoi_count: number; terminated_count: number }> => {
    const { data } = await api.get('/employees/stats/summary')
    return data
  },
}

// ============================================
// DASHBOARD
// ============================================

export const dashboard = {
  getStats: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/dashboard/stats')
    return data
  },

  getRecentActivity: async (limit?: number): Promise<RecentActivity> => {
    const { data } = await api.get('/dashboard/recent-activity', {
      params: { limit },
    })
    return data
  },
}

export default api
