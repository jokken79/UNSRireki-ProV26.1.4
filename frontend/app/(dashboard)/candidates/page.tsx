'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { candidates } from '@/lib/api'
import type { Candidate, CandidateStatus } from '@/types'
import Link from 'next/link'

const statusLabels: Record<CandidateStatus, string> = {
  registered: '登録済',
  presented: '紹介中',
  accepted: '採用決定',
  rejected: '不採用',
  processing: '手続中',
  hired: '入社済',
}

const statusColors: Record<CandidateStatus, string> = {
  registered: 'bg-gray-100 text-gray-800',
  presented: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  processing: 'bg-yellow-100 text-yellow-800',
  hired: 'bg-purple-100 text-purple-800',
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            履歴書管理
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            候補者の登録・管理
          </p>
        </div>
        <button
          onClick={() => {
            setEditingCandidate(null)
            setShowForm(true)
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新規登録
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="名前で検索..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
            >
              <option value="">全てのステータス</option>
              {Object.entries(statusLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-4 text-gray-500">読み込み中...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">
            データの取得に失敗しました
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      氏名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      国籍
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      電話番号
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      ステータス
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      登録日
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {data?.items.map((candidate) => (
                    <tr
                      key={candidate.id}
                      className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {candidate.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {candidate.full_name}
                          </div>
                          {candidate.name_kana && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {candidate.name_kana}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {candidate.nationality || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {candidate.mobile || candidate.phone || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            statusColors[candidate.status]
                          }`}
                        >
                          {statusLabels[candidate.status]}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(candidate.created_at).toLocaleDateString('ja-JP')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            href={`/candidates/${candidate.id}`}
                            className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                          >
                            詳細
                          </Link>
                          <button
                            onClick={() => {
                              setEditingCandidate(candidate)
                              setShowForm(true)
                            }}
                            className="text-gray-600 hover:text-gray-800 dark:text-gray-400"
                          >
                            編集
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  全 {data.total} 件中 {(page - 1) * 20 + 1} - {Math.min(page * 20, data.total)} 件
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 disabled:opacity-50"
                  >
                    前へ
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                    disabled={page === data.pages}
                    className="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 disabled:opacity-50"
                  >
                    次へ
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {candidate ? '候補者編集' : '新規候補者登録'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Info */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">基本情報</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  氏名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  フリガナ
                </label>
                <input
                  type="text"
                  name="name_kana"
                  value={formData.name_kana}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  ローマ字
                </label>
                <input
                  type="text"
                  name="name_romanji"
                  value={formData.name_romanji}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  性別
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                >
                  <option value="">選択してください</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  国籍
                </label>
                <input
                  type="text"
                  name="nationality"
                  value={formData.nationality}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  生年月日
                </label>
                <input
                  type="date"
                  name="birth_date"
                  value={formData.birth_date}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">連絡先</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  電話番号
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  携帯電話
                </label>
                <input
                  type="tel"
                  name="mobile"
                  value={formData.mobile}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  メールアドレス
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  郵便番号
                </label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  住所
                </label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
            </div>
          </div>

          {/* Visa Info */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">在留資格</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  在留資格
                </label>
                <input
                  type="text"
                  name="visa_type"
                  value={formData.visa_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  在留期限
                </label>
                <input
                  type="date"
                  name="visa_expiry"
                  value={formData.visa_expiry}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  日本語レベル
                </label>
                <select
                  name="japanese_level"
                  value={formData.japanese_level}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
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
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              備考
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium"
            >
              {isLoading ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
