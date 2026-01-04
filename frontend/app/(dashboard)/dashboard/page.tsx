'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Users,
  FileText,
  ClipboardList,
  UserCheck,
  AlertTriangle,
  TrendingUp,
  ArrowUpRight,
} from 'lucide-react'
import { dashboard } from '@/lib/api'
import { cn, formatDateJP } from '@/lib/utils'
import type { DashboardStats, RecentActivity } from '@/types'

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color,
}: {
  title: string
  value: number
  subtitle?: string
  icon: React.ElementType
  trend?: number
  color: 'blue' | 'green' | 'orange' | 'red'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    orange: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400',
    red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white mt-1">
            {value.toLocaleString()}
          </p>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={cn('p-3 rounded-xl', colorClasses[color])}>
          <Icon size={24} />
        </div>
      </div>
      {trend !== undefined && (
        <div className="flex items-center gap-1 mt-4 text-sm">
          <TrendingUp size={16} className="text-green-500" />
          <span className="text-green-500 font-medium">+{trend}%</span>
          <span className="text-slate-400">from last month</span>
        </div>
      )}
    </motion.div>
  )
}

function ActivityItem({
  type,
  title,
  subtitle,
  timestamp,
  status,
}: {
  type: string
  title: string
  subtitle?: string
  timestamp: string | null
  status: string
}) {
  const icons = {
    candidate: FileText,
    application: ClipboardList,
    approval: UserCheck,
  }
  const Icon = icons[type as keyof typeof icons] || FileText

  return (
    <div className="flex items-start gap-3 py-3">
      <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700">
        <Icon size={16} className="text-slate-500 dark:text-slate-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
          {title}
        </p>
        {subtitle && (
          <p className="text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>
        )}
      </div>
      <div className="text-right">
        <span className={cn('badge', status === 'approved' ? 'badge-success' : 'badge-info')}>
          {status}
        </span>
        {timestamp && (
          <p className="text-[10px] text-slate-400 mt-1">
            {formatDateJP(timestamp)}
          </p>
        )}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: dashboard.getStats,
  })

  const { data: activity, isLoading: activityLoading } = useQuery<RecentActivity>({
    queryKey: ['dashboard-activity'],
    queryFn: () => dashboard.getRecentActivity(10),
  })

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          ダッシュボード
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          UNS Rirekisho Pro - Human Resource Management
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="総候補者"
          value={stats?.candidates.total || 0}
          subtitle={`新規: ${stats?.candidates.new || 0}`}
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="保留中の申請"
          value={stats?.applications.pending || 0}
          icon={ClipboardList}
          color="orange"
        />
        <StatCard
          title="承認待ち"
          value={stats?.joining_notices.pending_approval || 0}
          subtitle="入社連絡票"
          icon={UserCheck}
          color="green"
        />
        <StatCard
          title="在籍社員"
          value={stats?.employees.total_active || 0}
          subtitle={`派遣: ${stats?.employees.haken || 0} / 請負: ${stats?.employees.ukeoi || 0}`}
          icon={Users}
          color="blue"
        />
      </div>

      {/* Alerts */}
      {stats?.alerts.visa_expiring_soon && stats.alerts.visa_expiring_soon > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-4 border-l-4 border-l-orange-500 bg-orange-50 dark:bg-orange-900/20"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-orange-500" size={24} />
            <div>
              <p className="font-medium text-orange-800 dark:text-orange-200">
                ビザ期限アラート
              </p>
              <p className="text-sm text-orange-700 dark:text-orange-300">
                {stats.alerts.visa_expiring_soon}名の社員のビザが90日以内に期限切れになります
              </p>
            </div>
            <button className="ml-auto btn-secondary text-sm flex items-center gap-1">
              確認する <ArrowUpRight size={14} />
            </button>
          </div>
        </motion.div>
      )}

      {/* Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            最近のアクティビティ
          </h2>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {activityLoading ? (
              <p className="text-slate-400 py-4">Loading...</p>
            ) : (
              <>
                {activity?.recent_candidates.slice(0, 3).map((item) => (
                  <ActivityItem
                    key={`candidate-${item.id}`}
                    type="candidate"
                    title={item.name || `候補者 #${item.id}`}
                    timestamp={item.timestamp}
                    status={item.status}
                  />
                ))}
                {activity?.recent_approvals.slice(0, 3).map((item) => (
                  <ActivityItem
                    key={`approval-${item.id}`}
                    type="approval"
                    title={item.name || `入社連絡票 #${item.id}`}
                    subtitle="入社連絡票承認"
                    timestamp={item.timestamp}
                    status={item.status}
                  />
                ))}
              </>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            クイックアクション
          </h2>
          <div className="space-y-3">
            <button className="w-full btn-primary flex items-center justify-center gap-2">
              <FileText size={18} />
              新規候補者を登録
            </button>
            <button className="w-full btn-secondary flex items-center justify-center gap-2">
              <ClipboardList size={18} />
              申請を確認
            </button>
            <button className="w-full btn-secondary flex items-center justify-center gap-2">
              <UserCheck size={18} />
              承認待ちを確認
            </button>
          </div>

          <hr className="my-6 border-slate-200 dark:border-slate-700" />

          <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
            サマリー
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">下書き入社連絡票</span>
              <span className="font-medium text-slate-900 dark:text-white">
                {stats?.joining_notices.draft || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">処理中の候補者</span>
              <span className="font-medium text-slate-900 dark:text-white">
                {stats?.candidates.pending || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
