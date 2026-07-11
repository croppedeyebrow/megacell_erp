import type { ReactNode } from 'react'
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { cn } from '@/lib/cn'

export type AlertTone = 'info' | 'success' | 'warning' | 'danger'

const icons = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: AlertCircle,
}

export function Alert({
  tone = 'info',
  title,
  children,
  className,
}: {
  tone?: AlertTone
  title?: string
  children: ReactNode
  className?: string
}) {
  const Icon = icons[tone]
  return (
    <div className={cn('alert', `alert--${tone}`, className)} role="alert">
      <Icon size={18} aria-hidden />
      <div className="alert__body">
        {title && <div className="alert__title">{title}</div>}
        <div>{children}</div>
      </div>
    </div>
  )
}
