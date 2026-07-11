import { cn } from '@/lib/cn'

export function Skeleton({
  width,
  height = 16,
  className,
}: {
  width?: number | string
  height?: number | string
  className?: string
}) {
  return (
    <span
      className={cn('skeleton', className)}
      style={{ width: width ?? '100%', height }}
      aria-hidden
    />
  )
}

export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="data-table-wrap" aria-busy aria-label="불러오는 중">
      <div style={{ padding: 16, display: 'grid', gap: 12 }}>
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 12 }}>
            {Array.from({ length: cols }).map((__, c) => (
              <Skeleton key={c} height={14} />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
