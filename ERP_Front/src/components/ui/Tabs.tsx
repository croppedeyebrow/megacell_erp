import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export function Tabs({
  tabs,
  value,
  onChange,
}: {
  tabs: Array<{ id: string; label: string }>
  value: string
  onChange: (id: string) => void
}) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={value === tab.id}
          className={cn('tab', value === tab.id && 'tab--active')}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

export function Panel({
  title,
  children,
  className,
}: {
  title?: string
  children: ReactNode
  className?: string
}) {
  return (
    <section className={cn('panel', className)}>
      {title && <h2 className="section-title">{title}</h2>}
      {children}
    </section>
  )
}
