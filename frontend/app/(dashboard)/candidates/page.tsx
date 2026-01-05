'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Plus,
  Search,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  UserCheck,
  Users,
  X,
  ChevronLeft,
  ChevronRight,
  Edit3,
  Eye
} from 'lucide-react'
import { candidates } from '@/lib/api'
import type { Candidate, CandidateStatus } from '@/types'
import Link from 'next/link'
import { cn } from '@/lib/utils'

const statusConfig: Record<CandidateStatus, { label: string; class: string; icon: React.ElementType }> = {
  registered: {
    label: '登録済',
    class: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-300 dark:border-slate-600',
    icon: FileText
  },
  presented: {
    label: '紹介中',
    class: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-300 dark:border-blue-700',
    icon: Clock
  },
  accepted: {
    label: '採用決定',
    class: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 border border-green-300 dark:border-green-700',
    icon: CheckCircle
  },
  rejected: {
    label: '不採用',
    class: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300 border border-red-300 dark:border-red-700',
    icon: XCircle
  },
  processing: {
    label: '手続中',
    class: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 border border-amber-300 dark:border-amber-700',
    icon: UserCheck
  },
  hired: {
    label: '入社済',
    class: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700',
    icon: Users
  },
}

function TableSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-800 dark:to-slate-700 px-6 py-4">
        <div className="flex gap-4">
          {[60, 150, 80, 100, 80, 80, 60].map((w, i) => (
            <div key={i} className="h-4 bg-slate-200 dark:bg-slate-600 rounded" style={{ width: w }} />
          ))}
        </div>
      </div>
      {[...Array(10)].map((_, i) => (
        <div key={i} className="px-6 py-5 border-b border-slate-100 dark:border-slate-800">
          <div className="flex gap-4 items-center">
            <div className="w-12 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
            <div className="flex-1">
              <div className="w-40 h-4 bg-slate-200 dark:bg-slate-700 rounded mb-2" />
              <div className="w-24 h-3 bg-slate-100 dark:bg-slate-800 rounded" />
            </div>
            <div className="w-16 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
            <div className="w-24 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
            <div className="w-20 h-6 bg-slate-200 dark:bg-slate-700 rounded-full" />
            <div className="w-20 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
            <div className="w-16 h-4 bg-slate-200 dark:bg-slate-700 rounded" />
          </div>
        </div>
      ))}
    </div>
  )
}

function StatusBadge({ status }: { status: CandidateStatus }) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-full shadow-sm', config.class)}>
      <Icon size={12} />
      {config.label}
    </span>
  )
}

export default function CandidatesPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingCandidate, setEditingCandidate] = useState<Candidate | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['candidates', page, search, statusFilter],
    queryFn: () =>
      candidates.list({
        page,
        page_size: 20,
        search: search || undefined,
        status: statusFilter || undefined,
      }),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<Candidate>) => candidates.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      setShowForm(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Candidate> }) =>
      candidates.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
      setEditingCandidate(null)
      setShowForm(false)
    },
  })

  const handleSubmit = (formData: Partial<Candidate>) => {
    if (editingCandidate) {
      updateMutation.mutate({ id: editingCandidate.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            履歴書管理
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">
            候補者の登録・管理
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => {
            setEditingCandidate(null)
            setShowForm(true)
          }}
          className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white rounded-xl font-semibold transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/40 flex items-center gap-2"
        >
          <Plus size={20} />
          新規登録
        </motion.button>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-6 border border-slate-200 dark:border-slate-700 backdrop-blur-sm bg-white/80 dark:bg-slate-800/80"
      >
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[250px] relative">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <Search size={18} className="text-slate-400" />
            </div>
            <input
              type="text"
              placeholder="名前で検索..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow shadow-sm hover:shadow-md"
            />
          </div>
          <div className="min-w-[200px]">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow shadow-sm hover:shadow-md appearance-none cursor-pointer"
            >
              <option value="">全てのステータス</option>
              {Object.entries(statusConfig).map(([value, { label }]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card overflow-hidden border border-slate-200 dark:border-slate-700 shadow-xl"
      >
        {isLoading ? (
          <TableSkeleton />
        ) : error ? (
          <div className="p-12 text-center">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle size={32} className="text-red-500" />
            </div>
            <p className="text-red-500 font-semibold">データの取得に失敗しました</p>
            <p className="text-slate-400 text-sm mt-2">ページを更新してください</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700 border-b-2 border-primary-200 dark:border-primary-800">
                  <tr>
                    {['ID', '氏名', '国籍', '電話番号', 'ステータス', '登録日', '操作'].map((header) => (
                      <th key={header} className="px-6 py-4 text-left text-xs font-bold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {data?.items.map((candidate, index) => (
                    <motion.tr
                      key={candidate.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.03 * index }}
                      className="group hover:bg-gradient-to-r hover:from-primary-50/50 hover:to-transparent dark:hover:from-primary-900/10 transition-all duration-200"
                    >
                      <td className="px-6 py-5 whitespace-nowrap text-sm font-mono text-slate-500 dark:text-slate-400">
                        #{candidate.id}
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap">
                        <div>
                          <div className="font-semibold text-slate-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                            {candidate.full_name}
                          </div>
                          {candidate.name_kana && (
                            <div className="text-xs text-slate-400 mt-0.5">
                              {candidate.name_kana}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap text-sm text-slate-700 dark:text-slate-300">
                        {candidate.nationality || '-'}
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap text-sm text-slate-700 dark:text-slate-300 font-mono">
                        {candidate.mobile || candidate.phone || '-'}
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap">
                        <StatusBadge status={candidate.status} />
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                        {new Date(candidate.created_at).toLocaleDateString('ja-JP')}
                      </td>
                      <td className="px-6 py-5 whitespace-nowrap">
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Link
                            href={`/candidates/${candidate.id}`}
                            className="p-2 rounded-lg bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 hover:bg-primary-100 dark:hover:bg-primary-900/50 transition-colors"
                            title="詳細"
                          >
                            <Eye size={16} />
                          </Link>
                          <button
                            onClick={() => {
                              setEditingCandidate(candidate)
                              setShowForm(true)
                            }}
                            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                            title="編集"
                          >
                            <Edit3 size={16} />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/50">
                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                  全 <span className="font-bold text-slate-700 dark:text-slate-200">{data.total.toLocaleString()}</span> 件中{' '}
                  <span className="font-bold text-slate-700 dark:text-slate-200">{(page - 1) * 20 + 1}</span> -{' '}
                  <span className="font-bold text-slate-700 dark:text-slate-200">{Math.min(page * 20, data.total)}</span> 件
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-1 font-medium"
                  >
                    <ChevronLeft size={16} />
                    前へ
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                    disabled={page === data.pages}
                    className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-1 font-medium"
                  >
                    次へ
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </motion.div>

      {/* Modal Form */}
      {showForm && (
        <CandidateFormModal
          candidate={editingCandidate}
          onClose={() => {
            setShowForm(false)
            setEditingCandidate(null)
          }}
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}
    </div>
  )
}

function CandidateFormModal({
  candidate,
  onClose,
  onSubmit,
  isLoading,
}: {
  candidate: Candidate | null
  onClose: () => void
  onSubmit: (data: Partial<Candidate>) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    full_name: candidate?.full_name || '',
    name_kana: candidate?.name_kana || '',
    name_romanji: candidate?.name_romanji || '',
    gender: candidate?.gender || '',
    nationality: candidate?.nationality || '',
    birth_date: candidate?.birth_date || '',
    phone: candidate?.phone || '',
    mobile: candidate?.mobile || '',
    email: candidate?.email || '',
    postal_code: candidate?.postal_code || '',
    address: candidate?.address || '',
    visa_type: candidate?.visa_type || '',
    visa_expiry: candidate?.visa_expiry || '',
    japanese_level: candidate?.japanese_level || '',
    notes: candidate?.notes || '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-700"
      >
        <div className="p-6 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between bg-gradient-to-r from-transparent to-primary-50/30 dark:to-primary-900/10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
            <div className="w-1.5 h-8 bg-primary-500 rounded-full"></div>
            {candidate ? '候補者編集' : '新規候補者登録'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-8 overflow-y-auto max-h-[calc(90vh-140px)]">
          {/* Basic Info */}
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <FileText size={20} className="text-primary-500" />
              基本情報
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  氏名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  フリガナ
                </label>
                <input
                  type="text"
                  name="name_kana"
                  value={formData.name_kana}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  ローマ字
                </label>
                <input
                  type="text"
                  name="name_romanji"
                  value={formData.name_romanji}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  性別
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                >
                  <option value="">選択してください</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  国籍
                </label>
                <input
                  type="text"
                  name="nationality"
                  value={formData.nationality}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  生年月日
                </label>
                <input
                  type="date"
                  name="birth_date"
                  value={formData.birth_date}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <Users size={20} className="text-primary-500" />
              連絡先
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  電話番号
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  携帯電話
                </label>
                <input
                  type="tel"
                  name="mobile"
                  value={formData.mobile}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  メールアドレス
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  郵便番号
                </label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  住所
                </label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
            </div>
          </div>

          {/* Visa Info */}
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <CheckCircle size={20} className="text-primary-500" />
              在留資格
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  在留資格
                </label>
                <input
                  type="text"
                  name="visa_type"
                  value={formData.visa_type}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  在留期限
                </label>
                <input
                  type="date"
                  name="visa_expiry"
                  value={formData.visa_expiry}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  日本語レベル
                </label>
                <select
                  name="japanese_level"
                  value={formData.japanese_level}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow"
                >
                  <option value="">選択してください</option>
                  <option value="N1">N1</option>
                  <option value="N2">N2</option>
                  <option value="N3">N3</option>
                  <option value="N4">N4</option>
                  <option value="N5">N5</option>
                  <option value="なし">なし</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
              備考
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-shadow resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-6 border-t border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 font-semibold transition-colors"
            >
              キャンセル
            </button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 disabled:from-primary-400 disabled:to-primary-500 text-white font-semibold shadow-lg shadow-primary-500/25 disabled:shadow-none transition-all"
            >
              {isLoading ? '保存中...' : '保存'}
            </motion.button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  )
}
