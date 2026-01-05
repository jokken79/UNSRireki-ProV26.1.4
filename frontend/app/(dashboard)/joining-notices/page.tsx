'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { joiningNotices, candidates } from '@/lib/api'
import type { JoiningNotice, JoiningNoticeStatus, EmploymentType, HousingType } from '@/types'
import Link from 'next/link'

const statusLabels: Record<JoiningNoticeStatus, string> = {
  draft: '下書き',
  pending: '承認待ち',
  approved: '承認済',
  rejected: '却下',
}

const statusColors: Record<JoiningNoticeStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

const employmentTypeLabels: Record<EmploymentType, string> = {
  haken: '派遣',
  ukeoi: '請負',
}

export default function JoiningNoticesPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingNotice, setEditingNotice] = useState<JoiningNotice | null>(null)
  const [rejectingNotice, setRejectingNotice] = useState<JoiningNotice | null>(null)

  const { data: notices, isLoading, error } = useQuery({
    queryKey: ['joining-notices', statusFilter],
    queryFn: () => joiningNotices.list({ status: statusFilter || undefined }),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<JoiningNotice>) => joiningNotices.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['joining-notices'] })
      setShowForm(false)
    },
  })

  const submitMutation = useMutation({
    mutationFn: (id: number) => joiningNotices.submit(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['joining-notices'] })
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => joiningNotices.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['joining-notices'] })
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      joiningNotices.reject(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['joining-notices'] })
      setRejectingNotice(null)
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">入社連絡票</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">入社手続きの管理・承認</p>
        </div>
        <button
          onClick={() => {
            setEditingNotice(null)
            setShowForm(true)
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新規作成
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
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

      {/* Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-4 text-gray-500">読み込み中...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">データの取得に失敗しました</div>
        ) : (
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
                    種別
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    派遣先/勤務先
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    ステータス
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    作成日
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {notices?.map((notice) => (
                  <tr
                    key={notice.id}
                    className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {notice.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">
                          {notice.full_name}
                        </div>
                        {notice.name_kana && (
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {notice.name_kana}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          notice.employment_type === 'haken'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        {employmentTypeLabels[notice.employment_type]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {notice.assignment_company || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          statusColors[notice.status]
                        }`}
                      >
                        {statusLabels[notice.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(notice.created_at).toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/joining-notices/${notice.id}`}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                        >
                          詳細
                        </Link>
                        {notice.status === 'draft' && (
                          <button
                            onClick={() => submitMutation.mutate(notice.id)}
                            disabled={submitMutation.isPending}
                            className="text-green-600 hover:text-green-800"
                          >
                            提出
                          </button>
                        )}
                        {notice.status === 'pending' && (
                          <>
                            <button
                              onClick={() => approveMutation.mutate(notice.id)}
                              disabled={approveMutation.isPending}
                              className="text-green-600 hover:text-green-800"
                            >
                              承認
                            </button>
                            <button
                              onClick={() => setRejectingNotice(notice)}
                              className="text-red-600 hover:text-red-800"
                            >
                              却下
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {notices?.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      データがありません
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Form Modal */}
      {showForm && (
        <JoiningNoticeFormModal
          notice={editingNotice}
          onClose={() => {
            setShowForm(false)
            setEditingNotice(null)
          }}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
      )}

      {/* Reject Modal */}
      {rejectingNotice && (
        <RejectModal
          notice={rejectingNotice}
          onClose={() => setRejectingNotice(null)}
          onSubmit={(reason) => rejectMutation.mutate({ id: rejectingNotice.id, reason })}
          isLoading={rejectMutation.isPending}
        />
      )}
    </div>
  )
}

function JoiningNoticeFormModal({
  notice,
  onClose,
  onSubmit,
  isLoading,
}: {
  notice: JoiningNotice | null
  onClose: () => void
  onSubmit: (data: Partial<JoiningNotice>) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    candidate_id: notice?.candidate_id || 0,
    employment_type: notice?.employment_type || 'haken' as EmploymentType,
    full_name: notice?.full_name || '',
    name_kana: notice?.name_kana || '',
    gender: notice?.gender || '',
    nationality: notice?.nationality || '',
    birth_date: notice?.birth_date || '',
    visa_type: notice?.visa_type || '',
    visa_expiry: notice?.visa_expiry || '',
    postal_code: notice?.postal_code || '',
    address: notice?.address || '',
    housing_type: notice?.housing_type || 'rental' as HousingType,
    assignment_company: notice?.assignment_company || '',
    assignment_location: notice?.assignment_location || '',
    job_description: notice?.job_description || '',
    hourly_rate: notice?.hourly_rate || 0,
    bank_name: notice?.bank_name || '',
    branch_name: notice?.branch_name || '',
    account_number: notice?.account_number || '',
    bank_account_name: notice?.bank_account_name || '',
  })

  const [candidateSearch, setCandidateSearch] = useState('')
  const { data: candidateResults } = useQuery({
    queryKey: ['candidates-search', candidateSearch],
    queryFn: () => candidates.list({ search: candidateSearch, page_size: 5 }),
    enabled: candidateSearch.length >= 2,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'hourly_rate' || name === 'candidate_id' ? Number(value) : value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const selectCandidate = (candidate: { id: number; full_name: string; name_kana?: string | null }) => {
    setFormData((prev) => ({
      ...prev,
      candidate_id: candidate.id,
      full_name: candidate.full_name,
      name_kana: candidate.name_kana || '',
    }))
    setCandidateSearch('')
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between sticky top-0 bg-white dark:bg-slate-800">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {notice ? '入社連絡票編集' : '新規入社連絡票'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Candidate Selection */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">候補者選択</h3>
            <div className="relative">
              <input
                type="text"
                placeholder="候補者を検索..."
                value={candidateSearch}
                onChange={(e) => setCandidateSearch(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
              />
              {candidateResults && candidateResults.items.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-slate-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                  {candidateResults.items.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => selectCandidate(c)}
                      className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-slate-600"
                    >
                      <div className="font-medium">{c.full_name}</div>
                      {c.name_kana && <div className="text-sm text-gray-500">{c.name_kana}</div>}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {formData.candidate_id > 0 && (
              <p className="mt-2 text-sm text-green-600">
                選択中: {formData.full_name} (ID: {formData.candidate_id})
              </p>
            )}
          </div>

          {/* Employment Type */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">雇用種別</h3>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="employment_type"
                  value="haken"
                  checked={formData.employment_type === 'haken'}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600"
                />
                <span>派遣社員</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="employment_type"
                  value="ukeoi"
                  checked={formData.employment_type === 'ukeoi'}
                  onChange={handleChange}
                  className="w-4 h-4 text-purple-600"
                />
                <span>請負社員</span>
              </label>
            </div>
          </div>

          {/* Personal Info */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">個人情報</h3>
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
            </div>
          </div>

          {/* Housing */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">住居</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  住居種別
                </label>
                <select
                  name="housing_type"
                  value={formData.housing_type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                >
                  <option value="shataku">社宅</option>
                  <option value="own">自宅</option>
                  <option value="rental">賃貸</option>
                  <option value="other">その他</option>
                </select>
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

          {/* Assignment */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">配属先</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  派遣先/勤務先
                </label>
                <input
                  type="text"
                  name="assignment_company"
                  value={formData.assignment_company}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  勤務地
                </label>
                <input
                  type="text"
                  name="assignment_location"
                  value={formData.assignment_location}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  業務内容
                </label>
                <input
                  type="text"
                  name="job_description"
                  value={formData.job_description}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  時給
                </label>
                <input
                  type="number"
                  name="hourly_rate"
                  value={formData.hourly_rate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
            </div>
          </div>

          {/* Bank Account */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">振込先口座</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  銀行名
                </label>
                <input
                  type="text"
                  name="bank_name"
                  value={formData.bank_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  支店名
                </label>
                <input
                  type="text"
                  name="branch_name"
                  value={formData.branch_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  口座番号
                </label>
                <input
                  type="text"
                  name="account_number"
                  value={formData.account_number}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  口座名義
                </label>
                <input
                  type="text"
                  name="bank_account_name"
                  value={formData.bank_account_name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
                />
              </div>
            </div>
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
              disabled={isLoading || formData.candidate_id === 0}
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

function RejectModal({
  notice,
  onClose,
  onSubmit,
  isLoading,
}: {
  notice: JoiningNotice
  onClose: () => void
  onSubmit: (reason: string) => void
  isLoading: boolean
}) {
  const [reason, setReason] = useState('')

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-md">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">入社連絡票の却下</h2>
          <p className="text-sm text-gray-500 mt-1">{notice.full_name}</p>
        </div>

        <div className="p-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            却下理由 <span className="text-red-500">*</span>
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            required
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
            placeholder="却下理由を入力してください..."
          />
        </div>

        <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700"
          >
            キャンセル
          </button>
          <button
            onClick={() => onSubmit(reason)}
            disabled={isLoading || !reason.trim()}
            className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-medium"
          >
            {isLoading ? '処理中...' : '却下する'}
          </button>
        </div>
      </div>
    </div>
  )
}
