import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { X } from 'lucide-react'
import { IconButton } from './IconButton'
import { cn } from '@/lib/cn'

type ToastTone = 'default' | 'success' | 'danger' | 'warning'

interface ToastItem {
  id: string
  message: string
  tone: ToastTone
}

interface ToastContextValue {
  toast: (message: string, tone?: ToastTone) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([])

  const dismiss = useCallback((id: string) => {
    setItems((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback(
    (message: string, tone: ToastTone = 'default') => {
      const id = crypto.randomUUID()
      setItems((prev) => [...prev, { id, message, tone }])
      window.setTimeout(() => dismiss(id), 4000)
    },
    [dismiss],
  )

  const value = useMemo(() => ({ toast }), [toast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-viewport" aria-live="polite">
        {items.map((item) => (
          <div
            key={item.id}
            className={cn('toast', item.tone !== 'default' && `toast--${item.tone}`)}
            role="status"
          >
            <span style={{ flex: 1 }}>{item.message}</span>
            <IconButton label="알림 닫기" onClick={() => dismiss(item.id)} size="sm">
              <X size={14} color="currentColor" />
            </IconButton>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
