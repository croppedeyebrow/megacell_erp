import type { Permission } from '@/types'
import { apiFetch } from '@/lib/api/auth'

export interface SalesOrderDto {
  id: string
  order_no: string
  customer_name: string
  product_name: string
  quantity: number | null
  unit: string | null
  order_amount: number | null
  due_date: string | null
  order_date: string | null
  status: string
  owner_name: string | null
  vendor_name: string | null
  memo: string | null
  shipped_date: string | null
  erp_modified: boolean
}

export interface SalesOrderListDto {
  items: SalesOrderDto[]
  total: number
  page: number
  page_size: number
}

export interface LegacyImportResult {
  job_id: string
  status: string
  source_path: string
  success_count: number
  warning_count: number
  fail_count: number
  message: string
}

export const salesApi = {
  list: (params: {
    page?: number
    pageSize?: number
    q?: string
    status?: string
  }) => {
    const search = new URLSearchParams()
    if (params.page) search.set('page', String(params.page))
    if (params.pageSize) search.set('page_size', String(params.pageSize))
    if (params.q) search.set('q', params.q)
    if (params.status) search.set('status', params.status)
    const qs = search.toString()
    return apiFetch<SalesOrderListDto>(`/api/v1/sales-orders${qs ? `?${qs}` : ''}`)
  },
  get: (id: string) => apiFetch<SalesOrderDto>(`/api/v1/sales-orders/${id}`),
  importLegacySqlite: (source_path?: string) =>
    apiFetch<LegacyImportResult>('/api/v1/admin/imports/legacy-sqlite', {
      method: 'POST',
      body: JSON.stringify({ source_path: source_path ?? null }),
    }),
}

export type { Permission }
