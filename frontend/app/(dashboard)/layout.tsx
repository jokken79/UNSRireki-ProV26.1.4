'use client'

import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/Sidebar'
import { auth } from '@/lib/api'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await auth.logout()
    } finally {
      router.push('/login')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <Sidebar onLogout={handleLogout} />
      <main className="ml-64 min-h-screen">
        <div className="p-6">{children}</div>
      </main>
    </div>
  )
}
