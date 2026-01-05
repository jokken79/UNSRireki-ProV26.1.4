'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { employees } from '@/lib/api'
import type { Employee } from '@/types'
import Link from 'next/link'

export default function UkeoiEmployeesPage() {
  const [search, setSearch] = useState('')

  const { data: employeeList, isLoading, error } = useQuery({
    queryKey: ['employees', 'ukeoi', search],
    queryFn: () => employees.list({ employment_type: 'ukeoi', search: search || undefined }),
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">請負社員</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">請負社員の一覧・管理</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex gap-4">
          <div className="flex-1 max-w-md">
            <input
              type="text"
              placeholder="名前で検索..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full mx-auto"></div>
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
                    社員番号
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    氏名
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    国籍
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    業務種別
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    時給
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    在留期限
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    ステータス
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {employeeList?.map((emp) => (
                  <EmployeeRow key={emp.id} employee={emp} />
                ))}
                {employeeList?.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                      データがありません
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

function EmployeeRow({ employee }: { employee: Employee }) {
  const assignment = employee.ukeoi_assignment
  const isVisaExpiringSoon = employee.visa_expiry &&
    new Date(employee.visa_expiry) <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)

  return (
    <tr className="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
        {employee.employee_number}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div>
          <div className="font-medium text-gray-900 dark:text-white">{employee.full_name}</div>
          {employee.name_kana && (
            <div className="text-sm text-gray-500 dark:text-gray-400">{employee.name_kana}</div>
          )}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
        {employee.nationality || '-'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
        {assignment?.job_type || '-'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
        {assignment?.hourly_rate ? `¥${assignment.hourly_rate.toLocaleString()}` : '-'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {employee.visa_expiry ? (
          <span className={`text-sm ${isVisaExpiringSoon ? 'text-red-600 font-medium' : 'text-gray-900 dark:text-white'}`}>
            {new Date(employee.visa_expiry).toLocaleDateString('ja-JP')}
            {isVisaExpiringSoon && (
              <span className="ml-2 inline-flex px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded-full">
                期限間近
              </span>
            )}
          </span>
        ) : (
          <span className="text-sm text-gray-500">-</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span
          className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
            employee.status === 'active'
              ? 'bg-green-100 text-green-800'
              : employee.status === 'terminated'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {employee.status === 'active' ? '在籍' : employee.status === 'terminated' ? '退職' : employee.status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
        <Link
          href={`/employees/${employee.id}`}
          className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
        >
          詳細
        </Link>
      </td>
    </tr>
  )
}
