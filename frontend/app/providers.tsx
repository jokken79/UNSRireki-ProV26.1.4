'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { Toaster } from 'sonner'
import { useAuth } from '@/lib/auth'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
            retry: (failureCount, error) => {
              // Don't retry on 401/403
              if (error instanceof Error && error.message.includes('401')) return false
              if (error instanceof Error && error.message.includes('403')) return false
              return failureCount < 3
            },
          },
          mutations: {
            retry: false,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <AuthInitializer />
      {children}
      <Toaster
        position="top-right"
        richColors
        closeButton
        expand={false}
        toastOptions={{
          duration: 4000,
          classNames: {
            toast: 'font-sans',
            success: 'bg-green-50 border-green-200',
            error: 'bg-red-50 border-red-200',
            warning: 'bg-yellow-50 border-yellow-200',
            info: 'bg-blue-50 border-blue-200',
          },
        }}
      />
    </QueryClientProvider>
  )
}

function AuthInitializer() {
  const checkAuth = useAuth((state) => state.checkAuth)

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return null
}
