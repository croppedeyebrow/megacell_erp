import { useEffect, useId, useRef, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { IconButton } from './IconButton'
import { Button } from './Button'
import { cn } from '@/lib/cn'

export function Modal({
  open,
  title,
  children,
  onClose,
  footer,
  size = 'md',
}: {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
  footer?: ReactNode
  size?: 'md' | 'lg'
}) {
  const titleId = useId()
  const previouslyFocused = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!open) return
    previouslyFocused.current = document.activeElement as HTMLElement
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      previouslyFocused.current?.focus()
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <div
        className={cn('modal', size === 'lg' && 'modal--lg')}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="modal__header">
          <h2 id={titleId} className="modal__title">
            {title}
          </h2>
          <IconButton label="닫기" onClick={onClose} size="sm">
            <X size={18} />
          </IconButton>
        </div>
        <div className="modal__body">{children}</div>
        {footer && <div className="modal__footer">{footer}</div>}
      </div>
    </div>
  )
}

export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel,
  confirmVariant = 'danger',
  onConfirm,
  onClose,
  loading,
}: {
  open: boolean
  title: string
  children: ReactNode
  confirmLabel: string
  confirmVariant?: 'primary' | 'danger'
  onConfirm: () => void
  onClose: () => void
  loading?: boolean
}) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onClose}
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={loading}>
            닫기
          </Button>
          <Button variant={confirmVariant} onClick={onConfirm} loading={loading}>
            {confirmLabel}
          </Button>
        </>
      }
    >
      {children}
    </Modal>
  )
}
