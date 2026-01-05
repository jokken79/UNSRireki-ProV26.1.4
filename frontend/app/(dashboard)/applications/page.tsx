'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { applications, candidates } from '@/lib/api'
import type { Application, ApplicationStatus } from '@/types'

const statusLabels: Record<ApplicationStatus, string> = {
  pending: '選考中',
  accepted: '採用',
  rejected: '不採用',
}

const statusColors: Record<ApplicationStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export default function ApplicationsPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [showResultModal, setShowResultModal] = useState<Application | null>(null)

  const { data: applicationList, isLoading, error } = useQuery({
    queryKey: ['applications', statusFilter],
    queryFn: () => applications.list({ status: statusFilter || undefined }),
  })

  const resultMutation = useMutation({
    mutationFn: ({ id, result }: { id: number; result: { status: string; result_notes?: string } }) =>
      applications.recordResult(id, result),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      setShowResultModal(null)
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">申請管理</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">派遣先への紹介・選考状況</p>
        </div>
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
                    候補者
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    派遣先
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    紹介日
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    ステータス
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    結果日
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {applicationList?.map((app) => (
                  <tr
                    key={app.id}
                    className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {app.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <CandidateName candidateId={app.candidate_id} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {app.client_company_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {app.presented_at
                        ? new Date(app.presented_at).toLocaleDateString('ja-JP')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          statusColors[app.status]
                        }`}
                      >
                        {statusLabels[app.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {app.result_at
                        ? new Date(app.result_at).toLocaleDateString('ja-JP')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      {app.status === 'pending' && (
                        <button
                          onClick={() => setShowResultModal(app)}
                          className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                        >
                          結果入力
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {applicationList?.length === 0 && (
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

      {/* Result Modal */}
      {showResultModal && (
        <ResultModal
          application={showResultModal}
          onClose={() => setShowResultModal(null)}
          onSubmit={(result) => {
            resultMutation.mutate({ id: showResultModal.id, result })
          }}
          isLoading={resultMutation.isPending}
        />
      )}
    </div>
  )
}

function CandidateName({ candidateId }: { candidateId: number }) {
  const { data } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => candidates.get(candidateId),
  })

  return (
    <span className="text-sm font-medium text-gray-900 dark:text-white">
      {data?.full_name || `候補者 #${candidateId}`}
    </span>
  )
}

function ResultModal({
  application,
  onClose,
  onSubmit,
  isLoading,
}: {
  application: Application
  onClose: () => void
  onSubmit: (result: { status: string; result_notes?: string }) => void
  isLoading: boolean
}) {
  const [status, setStatus] = useState<'accepted' | 'rejected'>('accepted')
  const [notes, setNotes] = useState('')

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-md">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">選考結果入力</h2>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              結果
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="status"
                  value="accepted"
                  checked={status === 'accepted'}
                  onChange={() => setStatus('accepted')}
                  className="w-4 h-4 text-green-600"
                />
                <span className="text-gray-900 dark:text-white">採用</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="status"
                  value="rejected"
                  checked={status === 'rejected'}
                  onChange={() => setStatus('rejected')}
                  className="w-4 h-4 text-red-600"
                />
                <span className="text-gray-900 dark:text-white">不採用</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              備考
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
              placeholder="選考に関するメモ..."
            />
          </div>
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
            onClick={() => onSubmit({ status, result_notes: notes || undefined })}
            disabled={isLoading}
            className={`px-4 py-2 rounded-lg text-white font-medium ${
              status === 'accepted'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            {isLoading ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  )
}
