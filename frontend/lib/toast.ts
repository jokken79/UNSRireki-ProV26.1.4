import { toast } from 'sonner'

// Japanese message helpers for consistent UI
export const showToast = {
  success: (message: string) => {
    toast.success(message)
  },

  error: (message: string) => {
    toast.error(message)
  },

  warning: (message: string) => {
    toast.warning(message)
  },

  info: (message: string) => {
    toast.info(message)
  },

  loading: (message: string) => {
    return toast.loading(message)
  },

  dismiss: (id?: string | number) => {
    toast.dismiss(id)
  },

  // Predefined messages for common actions
  saved: () => toast.success('保存しました'),
  created: () => toast.success('作成しました'),
  updated: () => toast.success('更新しました'),
  deleted: () => toast.success('削除しました'),
  submitted: () => toast.success('提出しました'),
  approved: () => toast.success('承認しました'),
  rejected: () => toast.success('却下しました'),

  // Error messages
  saveFailed: () => toast.error('保存に失敗しました'),
  loadFailed: () => toast.error('データの読み込みに失敗しました'),
  networkError: () => toast.error('ネットワークエラーが発生しました'),
  unauthorized: () => toast.error('認証が必要です'),
  forbidden: () => toast.error('権限がありません'),
  serverError: () => toast.error('サーバーエラーが発生しました'),

  // Custom promise handler
  promise: <T,>(
    promise: Promise<T>,
    messages: { loading: string; success: string; error: string }
  ) => {
    return toast.promise(promise, messages)
  },
}

export { toast }
