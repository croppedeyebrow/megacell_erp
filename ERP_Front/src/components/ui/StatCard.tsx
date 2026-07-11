import type { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/cn'

export function StatCard({
  label,
  value,
  meta,
  to,
  className,
}: {
  label: string
  value: string | number
  meta?: string
  to?: string
  className?: string
}) {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      className={cn('stat-card', className)}
      onClick={() => to && navigate(to)}
      disabled={!to}
      style={!to ? { cursor: 'default' } : undefined}
    >
      <span className="stat-card__label">{label}</span>
      <span className="stat-card__value">{value}</span>
      {meta && <span className="stat-card__meta">{meta}</span>}
    </button>
  )
}

export function DescriptionList({
  items,
}: {
  items: Array<{ label: string; value: ReactNode }>
}) {
  return (
    <dl className="desc-list">
      {items.map((item) => (
        <div key={item.label} style={{ display: 'contents' }}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  )
}
