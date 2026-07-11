import type { Permission, User } from '@/types'

export class ApiError extends Error {
  code: string
  status: number

  constructor(message: string, code: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

type ErrorBody = {
  detail?:
    | string
    | { code?: string; message?: string }
    | Array<{ msg?: string }>
  error?: { code?: string; message?: string }
}

async function parseError(res: Response): Promise<ApiError> {
  let message = '요청에 실패했습니다.'
  let code = 'REQUEST_FAILED'
  try {
    const body = (await res.json()) as ErrorBody
    if (typeof body.detail === 'string') {
      message = body.detail
    } else if (Array.isArray(body.detail)) {
      message = body.detail.map((d) => d.msg).filter(Boolean).join(', ') || message
    } else if (body.detail && typeof body.detail === 'object') {
      message = body.detail.message ?? message
      code = body.detail.code ?? code
    } else if (body.error) {
      message = body.error.message ?? message
      code = body.error.code ?? code
    }
  } catch {
    // ignore
  }
  return new ApiError(message, code, res.status)
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  headers.set('X-Requested-With', 'XMLHttpRequest')

  const res = await fetch(path, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (!res.ok) {
    throw await parseError(res)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

export interface AuthUserDto {
  id: string
  email: string
  name: string
  department: string
  role: User['role']
  permissions: Permission[]
  is_active: boolean
}

export function toUser(dto: AuthUserDto): User {
  return {
    id: dto.id,
    email: dto.email,
    name: dto.name,
    department: dto.department,
    role: dto.role,
    permissions: dto.permissions,
  }
}

export const authApi = {
  me: () => apiFetch<AuthUserDto>('/api/v1/auth/me'),
  login: (email: string, password: string) =>
    apiFetch<AuthUserDto>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: {
    email: string
    password: string
    name: string
    department: string
  }) =>
    apiFetch<AuthUserDto>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  logout: () =>
    apiFetch<{ message: string }>('/api/v1/auth/logout', { method: 'POST' }),
  changePassword: (current_password: string, new_password: string) =>
    apiFetch<{ message: string }>('/api/v1/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password, new_password }),
    }),
}
