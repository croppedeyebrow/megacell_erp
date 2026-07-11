import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'
import type { StatusTone } from '@/lib/status'
import { resolveStatus } from '@/lib/status'

export interface BadgeProps {
  children: ReactNode
  tone?: StatusTone
  withDot?: boolean
  className?: string
}

export function Badge({ children, tone = 'neutral', withDot = true, className }: BadgeProps) {
  return (
    <span className={cn('badge', `badge--${tone}`, className)}>
      {withDot && <span className="badge__dot" aria-hidden />}
      {children}
    </span>
  )
}

export function StatusBadge({ code, className }: { code: string; className?: string }) {
  const meta = resolveStatus(code)
  return (
    <Badge tone={meta.tone} className={className}>
      {meta.label}
    </Badge>
  )
}
