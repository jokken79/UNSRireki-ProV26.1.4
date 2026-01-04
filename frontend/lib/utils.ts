import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format date to Japanese format (YYYY年MM月DD日)
 */
export function formatDateJP(date: string | Date | null | undefined): string {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

/**
 * Format date to ISO format (YYYY-MM-DD)
 */
export function formatDateISO(date: string | Date | null | undefined): string {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  return d.toISOString().split('T')[0]
}

/**
 * Format currency to Japanese Yen
 */
export function formatYen(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) return ''
  return new Intl.NumberFormat('ja-JP', {
    style: 'currency',
    currency: 'JPY',
  }).format(amount)
}

/**
 * Calculate age from birth date
 */
export function calculateAge(birthDate: string | Date | null | undefined): number | null {
  if (!birthDate) return null
  const birth = new Date(birthDate)
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age
}

/**
 * Get status badge color class
 */
export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    // Candidate status
    registered: 'badge-info',
    presented: 'badge-warning',
    accepted: 'badge-success',
    rejected: 'badge-danger',
    processing: 'badge-warning',
    hired: 'badge-success',
    // Application status
    pending: 'badge-warning',
    // Joining notice status
    draft: 'badge-neutral',
    approved: 'badge-success',
    // Employee status
    '在職中': 'badge-success',
    '退社': 'badge-neutral',
  }
  return statusColors[status] || 'badge-neutral'
}

/**
 * Get status display text (Japanese)
 */
export function getStatusText(status: string): string {
  const statusTexts: Record<string, string> = {
    // Candidate status
    registered: '登録済み',
    presented: '提出済み',
    accepted: '合格',
    rejected: '不合格',
    processing: '処理中',
    hired: '入社済み',
    // Application status
    pending: '保留中',
    // Joining notice status
    draft: '下書き',
    approved: '承認済み',
    // Employee status
    active: '在職中',
    terminated: '退社',
  }
  return statusTexts[status] || status
}

/**
 * Get employment type display text
 */
export function getEmploymentTypeText(type: 'haken' | 'ukeoi'): string {
  return type === 'haken' ? '派遣社員' : '請負社員'
}

/**
 * Get housing type display text
 */
export function getHousingTypeText(type: string): string {
  const housingTypes: Record<string, string> = {
    shataku: '社宅',
    own: '自宅',
    rental: '賃貸',
    other: 'その他',
  }
  return housingTypes[type] || type
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string | null | undefined, length: number): string {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
