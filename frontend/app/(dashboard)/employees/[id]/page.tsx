'use client'

import { use } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employees } from '@/lib/api'
import Link from 'next/link'
import { useState } from 'react'
import { PhotoDisplay } from '@/components/ui/avatar-display'

export default function EmployeeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const employeeId = parseInt(id)
  const queryClient = useQueryClient()
  const [showTerminateModal, setShowTerminateModal] = useState(false)

  const { data: employee, isLoading, error } = useQuery({
    queryKey: ['employee', employeeId],
    queryFn: () => employees.get(employeeId),
    enabled: !isNaN(employeeId),
  })

  const terminateMutation = useMutation({
    mutationFn: (date: string) => employees.terminate(employeeId, date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee', employeeId] })
      setShowTerminateModal(false)
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (error || !employee) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">社員が見つかりません</p>
        <Link href="/employees/haken" className="text-blue-600 hover:underline mt-4 inline-block">
          一覧に戻る
        </Link>
      </div>
    )
  }

  const isHaken = employee.employment_type === 'haken'
  const assignment = isHaken ? employee.haken_assignment : employee.ukeoi_assignment

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col md:flex-row items-start gap-6">
          {/* Photo */}
          <PhotoDisplay
            photoUrl={employee.photo_url}
            name={employee.full_name}
          />

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-center gap-4 mb-2">
              <Link
                href={isHaken ? '/employees/haken' : '/employees/ukeoi'}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {employee.full_name}
                  </h1>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    isHaken ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                  }`}>
                    {isHaken ? '派遣' : '請負'}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    employee.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {employee.status === 'active' ? '在籍' : '退職'}
                  </span>
                </div>
                <p className="text-gray-500 dark:text-gray-400">
                  社員番号: {employee.employee_number}
                </p>
              </div>
            </div>

            {/* Quick Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
              <div>
                <span className="text-gray-500 dark:text-gray-400">国籍:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">{employee.nationality || '-'}</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">在留資格:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">{employee.visa_type || '-'}</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">入社日:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {employee.hire_date ? new Date(employee.hire_date).toLocaleDateString('ja-JP') : '-'}
                </span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">住居:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {employee.housing_type === 'shataku' ? '社宅' :
                   employee.housing_type === 'own' ? '自宅' :
                   employee.housing_type === 'rental' ? '賃貸' : '-'}
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 mt-4">
              {employee.status === 'active' && (
                <button
                  onClick={() => setShowTerminateModal(true)}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
                >
                  退職処理
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">基本情報</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">氏名</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.full_name}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">フリガナ</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.name_kana || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">性別</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.gender || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">国籍</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.nationality || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">生年月日</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {employee.birth_date ? new Date(employee.birth_date).toLocaleDateString('ja-JP') : '-'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">入社日</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {employee.hire_date ? new Date(employee.hire_date).toLocaleDateString('ja-JP') : '-'}
                </dd>
              </div>
            </dl>
          </div>

          {/* Visa Info */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">在留資格</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">在留資格</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.visa_type || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">在留期限</dt>
                <dd className={`font-medium ${
                  employee.visa_expiry && new Date(employee.visa_expiry) <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
                    ? 'text-red-600'
                    : 'text-gray-900 dark:text-white'
                }`}>
                  {employee.visa_expiry ? new Date(employee.visa_expiry).toLocaleDateString('ja-JP') : '-'}
                </dd>
              </div>
            </dl>
          </div>

          {/* Address */}
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">住所</h2>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">郵便番号</dt>
                <dd className="font-medium text-gray-900 dark:text-white">{employee.postal_code || '-'}</dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500 dark:text-gray-400">住居種別</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {employee.housing_type === 'shataku' ? '社宅' :
                   employee.housing_type === 'own' ? '自宅' :
                   employee.housing_type === 'rental' ? '賃貸' : '-'}
                </dd>
              </div>
              <div className="col-span-2">
                <dt className="text-sm text-gray-500 dark:text-gray-400">住所</dt>
                <dd className="font-medium text-gray-900 dark:text-white">
                  {employee.address || '-'}
                  {employee.building_name && ` ${employee.building_name}`}
                </dd>
              </div>
            </dl>
          </div>

          {/* Assignment Info */}
          {assignment && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                {isHaken ? '派遣先情報' : '業務情報'}
              </h2>
              <dl className="grid grid-cols-2 gap-4">
                {isHaken && employee.haken_assignment && (
                  <>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">派遣先</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.client_company || '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">勤務地</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.assignment_location || '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">配属ライン</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.assignment_line || '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">業務内容</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.job_description || '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">時給</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.hourly_rate
                          ? `¥${employee.haken_assignment.hourly_rate.toLocaleString()}`
                          : '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">請求単価</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.haken_assignment.billing_rate
                          ? `¥${employee.haken_assignment.billing_rate.toLocaleString()}`
                          : '-'}
                      </dd>
                    </div>
                  </>
                )}
                {!isHaken && employee.ukeoi_assignment && (
                  <>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">業務種別</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.ukeoi_assignment.job_type || '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">時給</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.ukeoi_assignment.hourly_rate
                          ? `¥${employee.ukeoi_assignment.hourly_rate.toLocaleString()}`
                          : '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">通勤距離</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.ukeoi_assignment.commute_distance
                          ? `${employee.ukeoi_assignment.commute_distance} km`
                          : '-'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-gray-500 dark:text-gray-400">交通費</dt>
                      <dd className="font-medium text-gray-900 dark:text-white">
                        {employee.ukeoi_assignment.transport_allowance
                          ? `¥${employee.ukeoi_assignment.transport_allowance.toLocaleString()}`
                          : '-'}
                      </dd>
                    </div>
                  </>
                )}
              </dl>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Social Insurance */}
          {assignment && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">社会保険</h2>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">加入状況</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {(isHaken ? employee.haken_assignment?.social_insurance_enrolled : employee.ukeoi_assignment?.social_insurance_enrolled)
                      ? '加入' : '未加入'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">健康保険</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {(isHaken ? employee.haken_assignment?.health_insurance : employee.ukeoi_assignment?.health_insurance)
                      ? `¥${(isHaken ? employee.haken_assignment?.health_insurance : employee.ukeoi_assignment?.health_insurance)?.toLocaleString()}`
                      : '-'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">厚生年金</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {(isHaken ? employee.haken_assignment?.pension : employee.ukeoi_assignment?.pension)
                      ? `¥${(isHaken ? employee.haken_assignment?.pension : employee.ukeoi_assignment?.pension)?.toLocaleString()}`
                      : '-'}
                  </dd>
                </div>
              </dl>
            </div>
          )}

          {/* Bank Account (Ukeoi only) */}
          {!isHaken && employee.ukeoi_assignment && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">振込先口座</h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-gray-500 dark:text-gray-400">銀行名</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {employee.ukeoi_assignment.bank_name || '-'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500 dark:text-gray-400">支店名</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {employee.ukeoi_assignment.branch_name || '-'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500 dark:text-gray-400">口座番号</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {employee.ukeoi_assignment.account_number || '-'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500 dark:text-gray-400">口座名義</dt>
                  <dd className="font-medium text-gray-900 dark:text-white">
                    {employee.ukeoi_assignment.bank_account_name || '-'}
                  </dd>
                </div>
              </dl>
            </div>
          )}

          {/* Notes */}
          {assignment && (isHaken ? employee.haken_assignment?.notes : employee.ukeoi_assignment?.notes) && (
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">備考</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {isHaken ? employee.haken_assignment?.notes : employee.ukeoi_assignment?.notes}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Terminate Modal */}
      {showTerminateModal && (
        <TerminateModal
          employeeName={employee.full_name}
          onClose={() => setShowTerminateModal(false)}
          onSubmit={(date) => terminateMutation.mutate(date)}
          isLoading={terminateMutation.isPending}
        />
      )}
    </div>
  )
}

function TerminateModal({
  employeeName,
  onClose,
  onSubmit,
  isLoading,
}: {
  employeeName: string
  onClose: () => void
  onSubmit: (date: string) => void
  isLoading: boolean
}) {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-md">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">退職処理</h2>
          <p className="text-sm text-gray-500 mt-1">{employeeName}</p>
        </div>

        <div className="p-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            退職日 <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700"
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
            onClick={() => onSubmit(date)}
            disabled={isLoading || !date}
            className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-medium"
          >
            {isLoading ? '処理中...' : '退職処理を実行'}
          </button>
        </div>
      </div>
    </div>
  )
}
