'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { auth as authApi } from './api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  setUser: (user: User | null) => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (username: string, password: string) => {
        try {
          await authApi.login({ username, password })
          const user = await authApi.getMe()

          // Set cookie for middleware
          document.cookie = `access_token=${localStorage.getItem('access_token')}; path=/; max-age=${60 * 30}; SameSite=Strict`

          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ user: null, isAuthenticated: false, isLoading: false })
          throw error
        }
      },

      logout: async () => {
        try {
          await authApi.logout()
        } finally {
          // Clear cookie
          document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ user: null, isAuthenticated: false, isLoading: false })
          return
        }

        try {
          const user = await authApi.getMe()
          // Refresh cookie
          document.cookie = `access_token=${token}; path=/; max-age=${60 * 30}; SameSite=Strict`
          set({ user, isAuthenticated: true, isLoading: false })
        } catch {
          // Token invalid, clear everything
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      setUser: (user) => set({ user, isAuthenticated: !!user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

// Role checking utilities
export function hasRole(user: User | null, roles: string[]): boolean {
  if (!user) return false
  return roles.includes(user.role)
}

export function isAdmin(user: User | null): boolean {
  return hasRole(user, ['super_admin', 'admin'])
}

export function isManager(user: User | null): boolean {
  return hasRole(user, ['super_admin', 'admin', 'manager'])
}

export function isStaff(user: User | null): boolean {
  return hasRole(user, ['super_admin', 'admin', 'manager', 'staff'])
}
