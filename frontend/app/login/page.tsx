'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { auth } from '@/lib/api'
import { Users } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await auth.login({ username, password })
      router.push('/dashboard')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'ログインに失敗しました')
      } else {
        setError('ログインに失敗しました')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="glass-card p-8 shadow-2xl">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-600 mb-4 shadow-lg shadow-primary-500/30 ring-4 ring-white/20 dark:ring-white/10">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
              UNS Rirekisho Pro
            </h1>
            <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium">
              人材派遣管理システム
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-4 rounded-lg bg-red-50/50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 backdrop-blur-sm">
                <p className="text-sm text-red-600 dark:text-red-400 font-medium">{error}</p>
              </div>
            )}

            <div>
              <label
                htmlFor="username"
                className="label"
              >
                ユーザー名
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="input"
                placeholder="ユーザー名を入力"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="label"
              >
                パスワード
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="input"
                placeholder="パスワードを入力"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  ログイン中...
                </>
              ) : (
                'ログイン'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-center text-xs text-gray-500 dark:text-gray-400">
              ユニバーサル企画株式会社
            </p>
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-1">
              Universal Kikaku Co., Ltd.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
