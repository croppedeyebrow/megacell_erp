export type Permission =
  | 'home.view'
  | 'sales.view'
  | 'sales.edit'
  | 'production.view'
  | 'production.edit'
  | 'purchasing.view'
  | 'inventory.view'
  | 'inventory.adjust'
  | 'as.view'
  | 'as.edit'
  | 'master.view'
  | 'analytics.view'
  | 'admin.view'
  | 'admin.manage'
  | 'document.generate'
  | 'report.export'

export interface User {
  id: string
  name: string
  email: string
  department: string
  role: 'viewer' | 'staff' | 'manager' | 'executive' | 'admin'
  permissions: Permission[]
}

export interface BreadcrumbItem {
  label: string
  to?: string
}

export interface PageAction {
  label: string
  onClick?: () => void
  to?: string
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  disabled?: boolean
  loading?: boolean
}

export interface ListQuery {
  page: number
  pageSize: number
  search?: string
  sort?: string
  filters?: Record<string, string>
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
