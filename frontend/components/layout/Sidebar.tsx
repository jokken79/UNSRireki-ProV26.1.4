'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FileText,
  ClipboardList,
  UserCheck,
  Building2,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Moon,
  Sun,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  name: string
  nameJP: string
  href: string
  icon: React.ReactNode
  badge?: number
}

const navItems: NavItem[] = [
  {
    name: 'Dashboard',
    nameJP: 'ダッシュボード',
    href: '/dashboard',
    icon: <LayoutDashboard size={20} />,
  },
  {
    name: 'Candidates',
    nameJP: '候補者 (履歴書)',
    href: '/candidates',
    icon: <FileText size={20} />,
  },
  {
    name: 'Applications',
    nameJP: '申請',
    href: '/applications',
    icon: <ClipboardList size={20} />,
  },
  {
    name: 'Joining Notices',
    nameJP: '入社連絡票',
    href: '/joining-notices',
    icon: <UserCheck size={20} />,
  },
  {
    name: 'Dispatch (派遣)',
    nameJP: '派遣社員',
    href: '/employees/haken',
    icon: <Users size={20} />,
  },
  {
    name: 'Contract (請負)',
    nameJP: '請負社員',
    href: '/employees/ukeoi',
    icon: <Briefcase size={20} />,
  },
  {
    name: 'Housing',
    nameJP: '社宅管理',
    href: '/housing',
    icon: <Building2 size={20} />,
  },
]

interface SidebarProps {
  onLogout: () => void
}

export function Sidebar({ onLogout }: SidebarProps) {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const [isDark, setIsDark] = useState(false)

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-50 flex flex-col bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transition-all duration-300',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200 dark:border-slate-700">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-lg">
              U
            </div>
            <div>
              <h1 className="font-bold text-slate-900 dark:text-white">UNS Rirekisho</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Pro v26.1</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-10 h-10 rounded-lg bg-primary-500 flex items-center justify-center text-white font-bold text-lg mx-auto">
            U
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            'p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400 transition-colors',
            collapsed && 'absolute -right-3 top-6 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm'
          )}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {!collapsed && (
          <p className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Menu
          </p>
        )}
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all relative group',
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 font-medium'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50'
              )}
            >
              <span className={cn(isActive && 'text-primary-500')}>{item.icon}</span>
              {!collapsed && (
                <span className="text-sm">{item.nameJP}</span>
              )}
              {isActive && !collapsed && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute right-3 w-1.5 h-1.5 rounded-full bg-primary-500"
                />
              )}
              {item.badge && !collapsed && (
                <span className="ml-auto bg-accent-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
              {collapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                  {item.nameJP}
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-slate-200 dark:border-slate-700 space-y-1">
        <button
          onClick={toggleTheme}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors'
          )}
        >
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
          {!collapsed && <span className="text-sm">{isDark ? 'ライトモード' : 'ダークモード'}</span>}
        </button>
        <Link
          href="/settings"
          className={cn(
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors'
          )}
        >
          <Settings size={20} />
          {!collapsed && <span className="text-sm">設定</span>}
        </Link>
        <button
          onClick={onLogout}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors'
          )}
        >
          <LogOut size={20} />
          {!collapsed && <span className="text-sm">ログアウト</span>}
        </button>
      </div>
    </aside>
  )
}
