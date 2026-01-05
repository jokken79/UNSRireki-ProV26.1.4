'use client'

import { use } from 'react'
import { useQuery } from '@tanstack/react-query'
import { candidates } from '@/lib/api'
import Link from 'next/link'
import type { CandidateStatus } from '@/types'

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

export default function CandidateDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const candidateId = parseInt(id)

  const { data: candidate, isLoading, error } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => candidates.get(candidateId),
    enabled: !isNaN(candidateId),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (error || !candidate) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">候補者が見つかりません</p>
        <Link href="/candidates" className="text-blue-600 hover:underline mt-4 inline-block">
          一覧に戻る
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/candidates"
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {candidate.full_name}
            </h1>
            {candidate.name_kana && (
              <p className="text-gray-500 dark:text-gray-400">{candidate.name_kana}</p>
            )}
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[candidate.status]}`}>
            {statusLabels[candidate.status]}
          </span>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/applications/new?candidate_id=${candidate.id}`}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
          >
            派遣先に紹介
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info Card */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">基本情報</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">氏名</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.full_name}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">ローマ字</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.name_romanji || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">性別</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.gender || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">国籍</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.nationality || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">生年月日</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.birth_date ? new Date(candidate.birth_date).toLocaleDateString('ja-JP') : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">婚姻状況</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.marital_status || '-'}</dd>
              </div>
            </dl>
          </div>

          {/* Contact Info Card */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">連絡先</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">電話番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.phone || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">携帯電話</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.mobile || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">メール</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.email || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">郵便番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.postal_code || '-'}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-sm text-gray-500 dark:text-gray-400">住所</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.address || '-'}
                  {candidate.building_name && ` ${candidate.building_name}`}
                </dd>
              </div>
            </dl>
          </div>

          {/* Visa Info Card */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">在留資格</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">在留資格</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.visa_type || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">在留期限</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.visa_expiry ? new Date(candidate.visa_expiry).toLocaleDateString('ja-JP') : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">在留カード番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.residence_card_number || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">パスポート番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.passport_number || '-'}</dd>
              </div>
            </dl>
          </div>

          {/* Physical Info */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">身体情報</h2>
            <dl className="grid grid-cols-3 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">身長</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.height ? `${candidate.height} cm` : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">体重</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.weight ? `${candidate.weight} kg` : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">靴サイズ</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {candidate.shoe_size ? `${candidate.shoe_size} cm` : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">血液型</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.blood_type || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">利き手</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.dominant_hand || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">制服サイズ</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.uniform_size || '-'}</dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Japanese Level */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">日本語能力</h2>
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-400">レベル</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.japanese_level || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-400">聴解</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.listening_level || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-400">会話</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.speaking_level || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-400">読解</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.reading_level || '-'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-400">作文</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.writing_level || '-'}</dd>
              </div>
            </dl>
          </div>

          {/* Emergency Contact */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">緊急連絡先</h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">氏名</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.emergency_contact_name || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">続柄</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.emergency_contact_relation || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">電話番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{candidate.emergency_contact_phone || '-'}</dd>
              </div>
            </dl>
          </div>

          {/* Documents */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">書類</h2>
            {candidate.documents && candidate.documents.length > 0 ? (
              <ul className="space-y-2">
                {candidate.documents.map((doc) => (
                  <li key={doc.id}>
                    <a
                      href={doc.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 text-blue-600"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      <span className="text-sm">{doc.file_name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">書類がありません</p>
            )}
          </div>

          {/* Notes */}
          {candidate.notes && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">備考</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{candidate.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
