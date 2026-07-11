import { useMemo, type ReactNode } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { IconButton } from '@/components/ui/IconButton'
import { SearchField } from '@/components/ui/SearchField'
import { Select } from '@/components/ui/Select'
import { EmptyState } from '@/components/ui/EmptyState'
import { TableSkeleton } from '@/components/ui/Skeleton'
import { Alert } from '@/components/ui/Alert'
import { cn } from '@/lib/cn'

export interface DataTableColumn<T> {
  id: string
  header: string
  accessor: (row: T) => ReactNode
  align?: 'left' | 'right'
  width?: string | number
  sortable?: boolean
}

export interface FilterDef {
  id: string
  label: string
  options: Array<{ value: string; label: string }>
}

export interface DataTableProps<T> {
  columns: DataTableColumn<T>[]
  rows: T[]
  total: number
  rowKey: (row: T) => string
  loading?: boolean
  error?: string | null
  onRetry?: () => void
  searchPlaceholder?: string
  filters?: FilterDef[]
  emptyTitle?: string
  emptyDescription?: string
  emptyActionLabel?: string
  onEmptyAction?: () => void
  filteredEmpty?: boolean
  density?: 'default' | 'compact'
  toolbarExtra?: ReactNode
  bulkActions?: ReactNode
  selectedKeys?: string[]
  onSelectionChange?: (keys: string[]) => void
  getRowHref?: (row: T) => string | undefined
}

function useListParams() {
  const [params, setParams] = useSearchParams()
  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('pageSize') ?? '20') || 20
  const search = params.get('q') ?? ''
  const sort = params.get('sort') ?? ''

  const filters = useMemo(() => {
    const result: Record<string, string> = {}
    params.forEach((value, key) => {
      if (key.startsWith('f.')) result[key.slice(2)] = value
    })
    return result
  }, [params])

  const setQuery = (patch: Record<string, string | null>) => {
    const next = new URLSearchParams(params)
    Object.entries(patch).forEach(([key, value]) => {
      if (value == null || value === '') next.delete(key)
      else next.set(key, value)
    })
    if (!('page' in patch)) next.set('page', '1')
    setParams(next, { replace: true })
  }

  return { page, pageSize, search, sort, filters, setQuery, params, setParams }
}

export function DataTable<T>({
  columns,
  rows,
  total,
  rowKey,
  loading,
  error,
  onRetry,
  searchPlaceholder = '업무번호, 거래처, 품목명 검색',
  filters = [],
  emptyTitle = '데이터가 없습니다',
  emptyDescription = '조건에 맞는 데이터가 없습니다.',
  emptyActionLabel,
  onEmptyAction,
  filteredEmpty,
  density = 'default',
  toolbarExtra,
  bulkActions,
  selectedKeys,
  onSelectionChange,
  getRowHref,
}: DataTableProps<T>) {
  const { page, pageSize, search, sort, filters: activeFilters, setQuery } =
    useListParams()

  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const selectable = !!onSelectionChange
  const allSelected =
    selectable && rows.length > 0 && rows.every((r) => selectedKeys?.includes(rowKey(r)))

  const chipEntries = Object.entries(activeFilters).filter(([, v]) => v)

  if (loading) return <TableSkeleton cols={columns.length} />

  if (error) {
    return (
      <Alert tone="danger" title="목록을 불러오지 못했습니다">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 8 }}>
          <span>{error}</span>
          {onRetry && (
            <Button size="sm" variant="secondary" onClick={onRetry}>
              다시 시도
            </Button>
          )}
        </div>
      </Alert>
    )
  }

  return (
    <div className="data-table-wrap">
      <div className="data-table-toolbar">
        <div className="filter-bar">
          <SearchField
            label="검색"
            value={search}
            placeholder={searchPlaceholder}
            onChange={(e) => setQuery({ q: e.target.value || null })}
          />
          {filters.map((filter) => (
            <Select
              key={filter.id}
              label={filter.label}
              options={filter.options}
              placeholder="전체"
              value={activeFilters[filter.id] ?? ''}
              onChange={(e) =>
                setQuery({ [`f.${filter.id}`]: e.target.value || null })
              }
              style={{ minWidth: 140 }}
            />
          ))}
          {(search || chipEntries.length > 0) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const clear: Record<string, null> = { q: null }
                filters.forEach((f) => {
                  clear[`f.${f.id}`] = null
                })
                setQuery(clear)
              }}
            >
              필터 초기화
            </Button>
          )}
        </div>
        {toolbarExtra}
      </div>

      {chipEntries.length > 0 && (
        <div className="filter-chips">
          {chipEntries.map(([key, value]) => {
            const def = filters.find((f) => f.id === key)
            const label =
              def?.options.find((o) => o.value === value)?.label ?? value
            return (
              <span key={key} className="filter-chip">
                {def?.label ?? key}: {label}
                <button
                  type="button"
                  aria-label={`${def?.label ?? key} 필터 제거`}
                  onClick={() => setQuery({ [`f.${key}`]: null })}
                >
                  <X size={12} />
                </button>
              </span>
            )
          })}
        </div>
      )}

      {selectable && selectedKeys && selectedKeys.length > 0 && (
        <div
          style={{
            padding: '8px 16px',
            background: 'var(--color-primary-50)',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            fontSize: 13,
          }}
        >
          <span>현재 페이지에서 {selectedKeys.length}건 선택됨</span>
          {bulkActions}
        </div>
      )}

      {rows.length === 0 ? (
        <EmptyState
          title={
            filteredEmpty || search || chipEntries.length
              ? '검색 결과가 없습니다'
              : emptyTitle
          }
          description={
            filteredEmpty || search || chipEntries.length
              ? '필터를 해제하거나 검색어를 수정해 보세요.'
              : emptyDescription
          }
          actionLabel={
            filteredEmpty || search || chipEntries.length
              ? undefined
              : emptyActionLabel
          }
          onAction={onEmptyAction}
        />
      ) : (
        <div className="table-scroll">
          <table
            className={cn(
              'data-table',
              density === 'compact' && 'data-table--compact',
            )}
          >
            <thead>
              <tr>
                {selectable && (
                  <th style={{ width: 40 }}>
                    <input
                      type="checkbox"
                      aria-label="현재 페이지 전체 선택"
                      checked={allSelected}
                      onChange={(e) => {
                        if (!onSelectionChange) return
                        onSelectionChange(
                          e.target.checked ? rows.map(rowKey) : [],
                        )
                      }}
                    />
                  </th>
                )}
                {columns.map((col) => {
                  const isSorted = sort === col.id || sort === `-${col.id}`
                  const asc = sort === col.id
                  return (
                    <th
                      key={col.id}
                      style={{ width: col.width, textAlign: col.align }}
                      aria-sort={
                        isSorted ? (asc ? 'ascending' : 'descending') : 'none'
                      }
                    >
                      {col.sortable ? (
                        <button
                          type="button"
                          className="btn btn--ghost btn--sm"
                          style={{ padding: 0, height: 'auto' }}
                          onClick={() =>
                            setQuery({
                              sort: asc ? `-${col.id}` : col.id,
                            })
                          }
                        >
                          {col.header}
                          {isSorted ? (asc ? ' ↑' : ' ↓') : ''}
                        </button>
                      ) : (
                        col.header
                      )}
                    </th>
                  )
                })}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const key = rowKey(row)
                const href = getRowHref?.(row)
                return (
                  <tr key={key}>
                    {selectable && (
                      <td>
                        <input
                          type="checkbox"
                          aria-label="행 선택"
                          checked={selectedKeys?.includes(key) ?? false}
                          onChange={(e) => {
                            if (!onSelectionChange || !selectedKeys) return
                            onSelectionChange(
                              e.target.checked
                                ? [...selectedKeys, key]
                                : selectedKeys.filter((k) => k !== key),
                            )
                          }}
                        />
                      </td>
                    )}
                    {columns.map((col, idx) => {
                      const content = col.accessor(row)
                      return (
                        <td
                          key={col.id}
                          className={cn(
                            col.align === 'right' && 'cell-right',
                            col.id === 'actions' && 'cell-actions',
                          )}
                        >
                          {idx === 0 && href ? (
                            <Link to={href} className="row-link">
                              {content}
                            </Link>
                          ) : (
                            content
                          )}
                        </td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <span>
          전체 {total.toLocaleString('ko-KR')}건 · {page}/{totalPages} 페이지
        </span>
        <div className="pagination__controls">
          <Select
            label="페이지 크기"
            hideLabel
            options={[
              { value: '10', label: '10건' },
              { value: '20', label: '20건' },
              { value: '50', label: '50건' },
            ]}
            value={String(pageSize)}
            onChange={(e) => setQuery({ pageSize: e.target.value, page: '1' })}
            style={{ width: 100 }}
          />
          <IconButton
            label="이전 페이지"
            size="sm"
            disabled={page <= 1}
            onClick={() => setQuery({ page: String(page - 1) })}
          >
            <ChevronLeft size={16} />
          </IconButton>
          <IconButton
            label="다음 페이지"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setQuery({ page: String(page + 1) })}
          >
            <ChevronRight size={16} />
          </IconButton>
        </div>
      </div>
    </div>
  )
}
