import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'

/** URL query 기반 클라이언트 필터·페이지 (API 연동 전 mock용) */
export function useClientList<T>(
  items: T[],
  searchFields: Array<(item: T) => string>,
  filterFields?: Record<string, (item: T) => string>,
) {
  const [params] = useSearchParams()
  const page = Number(params.get('page') ?? '1') || 1
  const pageSize = Number(params.get('pageSize') ?? '20') || 20
  const search = (params.get('q') ?? '').trim().toLowerCase()
  const sort = params.get('sort') ?? ''
  const filterKey = [...params.entries()]
    .filter(([k]) => k.startsWith('f.'))
    .map(([k, v]) => `${k}=${v}`)
    .join('&')

  return useMemo(() => {
    const filters: Record<string, string> = {}
    filterKey.split('&').filter(Boolean).forEach((pair) => {
      const [k, v] = pair.split('=')
      if (k?.startsWith('f.')) filters[k.slice(2)] = decodeURIComponent(v ?? '')
    })

    let result = [...items]

    if (search) {
      result = result.filter((item) =>
        searchFields.some((fn) => fn(item).toLowerCase().includes(search)),
      )
    }

    Object.entries(filters).forEach(([key, value]) => {
      const getter = filterFields?.[key]
      if (getter && value) {
        result = result.filter((item) => getter(item) === value)
      }
    })

    if (sort) {
      const desc = sort.startsWith('-')
      const field = desc ? sort.slice(1) : sort
      result.sort((a, b) => {
        const av = String((a as Record<string, unknown>)[field] ?? '')
        const bv = String((b as Record<string, unknown>)[field] ?? '')
        return desc ? bv.localeCompare(av, 'ko') : av.localeCompare(bv, 'ko')
      })
    }

    const total = result.length
    const start = (page - 1) * pageSize
    const pageItems = result.slice(start, start + pageSize)

    return {
      items: pageItems,
      total,
      filteredEmpty: total === 0 && (!!search || Object.keys(filters).length > 0),
    }
    // searchFields/filterFields는 호출부에서 안정적인 참조를 권장
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items, page, pageSize, search, sort, filterKey])
}
