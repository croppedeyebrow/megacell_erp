import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import type { BreadcrumbItem, PageAction } from '@/types'
import { Button } from '@/components/ui/Button'
import { useNavigate } from 'react-router-dom'

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="breadcrumb" aria-label="경로">
      {items.map((item, index) => {
        const isLast = index === items.length - 1
        return (
          <span key={`${item.label}-${index}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            {index > 0 && (
              <ChevronRight size={14} className="breadcrumb__sep" aria-hidden />
            )}
            {item.to && !isLast ? (
              <Link to={item.to}>{item.label}</Link>
            ) : (
              <span aria-current={isLast ? 'page' : undefined}>{item.label}</span>
            )}
          </span>
        )
      })}
    </nav>
  )
}

export function PageHeader({
  title,
  description,
  breadcrumbs,
  actions,
  status,
  meta,
}: {
  title: string
  description?: string
  breadcrumbs?: BreadcrumbItem[]
  actions?: PageAction[]
  status?: ReactNode
  meta?: ReactNode
}) {
  const navigate = useNavigate()

  return (
    <div>
      {breadcrumbs && breadcrumbs.length > 0 && <Breadcrumb items={breadcrumbs} />}
      <div className="page-header">
        <div>
          <div className="page-header__title-row">
            <h1 className="page-header__title">{title}</h1>
            {status}
          </div>
          {description && <p className="page-header__desc">{description}</p>}
          {meta && <div className="meta-row" style={{ marginTop: 8 }}>{meta}</div>}
        </div>
        {actions && actions.length > 0 && (
          <div className="page-header__actions">
            {actions.map((action) => (
              <Button
                key={action.label}
                variant={action.variant ?? 'secondary'}
                disabled={action.disabled}
                loading={action.loading}
                onClick={() => {
                  if (action.to) navigate(action.to)
                  else action.onClick?.()
                }}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
