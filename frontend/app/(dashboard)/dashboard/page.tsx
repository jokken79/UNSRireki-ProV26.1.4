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
  Plus,
  ArrowRight,
} from 'lucide-react'
import { dashboard } from '@/lib/api'
import { cn, formatDateJP } from '@/lib/utils'
import type { DashboardStats, RecentActivity } from '@/types'
import { TrendChart } from '@/components/dashboard/TrendChart'
import { DistributionChart } from '@/components/dashboard/DistributionChart'

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color,
  delay = 0,
}: {
  title: string
  value: number
  subtitle?: string
  icon: React.ElementType
  trend?: number
  color: 'blue' | 'green' | 'orange' | 'red' | 'purple'
  delay?: number
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-900',
    green: 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-200 dark:border-green-900',
    orange: 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-900',
    red: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-200 dark:border-red-900',
    purple: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-900',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="card p-6 relative overflow-hidden group hover:shadow-lg transition-all duration-300 border border-slate-100 dark:border-slate-800"
    >
      <div className={cn("absolute top-0 right-0 w-32 h-32 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110", colorClasses[color].split(' ')[0])} />

      <div className="relative z-10 flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-4xl font-bold text-slate-900 dark:text-white mt-2 tracking-tight">
            {value.toLocaleString()}
          </p>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1 font-medium">{subtitle}</p>
          )}
        </div>
        <div className={cn('p-3 rounded-xl border backdrop-blur-sm', colorClasses[color])}>
          <Icon size={24} />
        </div>
      </div>
      {trend !== undefined && (
        <div className="relative z-10 flex items-center gap-1 mt-4 text-sm">
          <div className="bg-green-50 dark:bg-green-900/30 px-2 py-0.5 rounded-full flex items-center gap-1">
            <TrendingUp size={14} className="text-green-600 dark:text-green-400" />
            <span className="text-green-600 dark:text-green-400 font-bold">+{trend}%</span>
          </div>
          <span className="text-slate-400 text-xs ml-1">先月比</span>
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
  index
}: {
  type: string
  title: string
  subtitle?: string
  timestamp: string | null
  status: string
  index: number
}) {
  const icons = {
    candidate: FileText,
    application: ClipboardList,
    approval: UserCheck,
  }
  const Icon = icons[type as keyof typeof icons] || FileText

  const statusColors = {
    approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 border-green-200',
    pending: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200',
    rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 border-red-200',
    draft: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200',
  }

  const badgeClass = statusColors[status as keyof typeof statusColors] || statusColors.draft

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 * index }}
      className="flex items-center gap-4 py-4 px-2 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-xl transition-colors group cursor-pointer"
    >
      <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">
        <Icon size={18} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
          {title}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>
          )}
          <span className="text-[10px] text-slate-300 dark:text-slate-600">•</span>
          {timestamp && (
            <p className="text-xs text-slate-400">
              {formatDateJP(timestamp)}
            </p>
          )}
        </div>
      </div>
      <div className="text-right">
        <span className={cn('px-2.5 py-1 rounded-full text-xs font-medium border', badgeClass)}>
          {status}
        </span>
      </div>
    </motion.div>
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
      <div className="flex items-center justify-center h-[calc(100vh-100px)]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-200 border-t-primary-500" />
          <p className="text-slate-400 animate-pulse">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            ダッシュボード
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            UNS Rirekisho Pro - Human Resource Management System
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-500 bg-white dark:bg-slate-800 px-3 py-1.5 rounded-full border shadow-sm">
            {new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' })}
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="総候補者"
          value={stats?.candidates.total || 0}
          subtitle={`新規登録: ${stats?.candidates.new || 0}名`}
          icon={FileText}
          color="blue"
          delay={0}
          trend={12}
        />
        <StatCard
          title="保留中の申請"
          value={stats?.applications.pending || 0}
          icon={ClipboardList}
          color="orange"
          delay={0.1}
        />
        <StatCard
          title="承認待ち連絡票"
          value={stats?.joining_notices.pending_approval || 0}
          subtitle="早急な確認が必要です"
          icon={UserCheck}
          color="red"
          delay={0.2}
        />
        <StatCard
          title="在籍社員数"
          value={stats?.employees.total_active || 0}
          subtitle={`派遣: ${stats?.employees.haken || 0} / 請負: ${stats?.employees.ukeoi || 0}`}
          icon={Users}
          color="green"
          delay={0.3}
        />
      </div>

      {/* Alerts */}
      {stats?.alerts.visa_expiring_soon && stats.alerts.visa_expiring_soon > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl p-4 border border-orange-200 bg-orange-50 dark:bg-orange-900/10 dark:border-orange-900/50 shadow-sm"
        >
          <div className="flex items-start md:items-center gap-4">
            <div className="p-2 bg-white dark:bg-orange-900/30 rounded-full shadow-sm text-orange-500">
              <AlertTriangle size={24} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-orange-900 dark:text-orange-100 flex items-center gap-2">
                ビザ期限アラート
                <span className="bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200 text-xs px-2 py-0.5 rounded-full">重要</span>
              </h3>
              <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                <span className="font-bold">{stats.alerts.visa_expiring_soon}名</span>の社員のビザが90日以内に期限切れになります。更新手続きを確認してください。
              </p>
            </div>
            <button className="btn-white text-orange-600 text-sm font-medium shrink-0 shadow-sm border-orange-100 hover:bg-orange-50">
              詳細を確認 <ArrowRight size={16} className="ml-1 inline" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TrendChart />
        </div>
        <div className="lg:col-span-1">
          <DistributionChart />
        </div>
      </div>

      {/* Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <div className="w-1 h-5 bg-primary-500 rounded-full" />
              最近のアクティビティ
            </h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">すべて見る</button>
          </div>

          <div className="divide-y divide-slate-100 dark:divide-slate-800/50">
            {activityLoading ? (
              <p className="text-slate-400 py-4 text-center">読み込み中...</p>
            ) : (
              <>
                {activity?.recent_candidates.slice(0, 3).map((item, i) => (
                  <ActivityItem
                    key={`candidate-${item.id}`}
                    index={i}
                    type="candidate"
                    title={item.name || `候補者 #${item.id}`}
                    subtitle="新規登録"
                    timestamp={item.timestamp}
                    status={item.status}
                  />
                ))}
                {activity?.recent_approvals.slice(0, 3).map((item, i) => (
                  <ActivityItem
                    key={`approval-${item.id}`}
                    index={i + 3}
                    type="approval"
                    title={item.name || `連絡票 #${item.id}`}
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
        <div className="card p-6 flex flex-col h-full">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <div className="w-1 h-5 bg-secondary-500 rounded-full" />
            クイックアクション
          </h2>

          <div className="space-y-4 flex-1">
            <button className="w-full btn-primary py-4 justify-between group shadow-lg shadow-primary-500/20">
              <span className="flex items-center gap-3">
                <span className="bg-white/20 p-1.5 rounded-lg"><Plus size={18} /></span>
                新規候補者を登録
              </span>
              <ArrowRight size={18} className="opacity-60 group-hover:translate-x-1 transition-transform" />
            </button>
            <div className="grid grid-cols-2 gap-4">
              <button className="w-full btn-secondary py-3 flex-col items-center gap-2 text-center h-auto hover:bg-slate-50 dark:hover:bg-slate-800">
                <ClipboardList size={24} className="text-slate-400 mb-1" />
                <span className="text-xs">申請確認</span>
              </button>
              <button className="w-full btn-secondary py-3 flex-col items-center gap-2 text-center h-auto hover:bg-slate-50 dark:hover:bg-slate-800">
                <UserCheck size={24} className="text-slate-400 mb-1" />
                <span className="text-xs">承認待ち</span>
              </button>
            </div>
          </div>

          <div className="mt-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-100 dark:border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              今月のサマリー
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-600 dark:text-slate-300">下書き中の連絡票</span>
                <span className="font-bold text-slate-900 dark:text-white bg-white dark:bg-slate-700 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-600 shadow-sm">
                  {stats?.joining_notices.draft || 0}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-600 dark:text-slate-300">選考中の候補者</span>
                <span className="font-bold text-slate-900 dark:text-white bg-white dark:bg-slate-700 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-600 shadow-sm">
                  {stats?.candidates.pending || 0}
                </span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <button className="text-xs text-primary-600 font-medium hover:underline flex items-center justify-center w-full gap-1">
                レポート詳細ページへ <ArrowUpRight size={10} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
