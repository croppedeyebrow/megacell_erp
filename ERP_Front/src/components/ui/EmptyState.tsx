import type { ReactNode } from 'react'
import { Inbox } from 'lucide-react'
import { Button } from './Button'

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
}: {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  icon?: ReactNode
}) {
  return (
    <div className="empty-state" role="status">
      {icon ?? <Inbox size={40} aria-hidden />}
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__desc">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
