import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { Permission, User } from '@/types'
import { ApiError, authApi, toUser } from '@/lib/api/auth'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  bootstrapping: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: {
    email: string
    password: string
    name: string
    department: string
  }) => Promise<void>
  logout: () => Promise<void>
  changePassword: (current: string, next: string) => Promise<void>
  hasPermission: (permission?: Permission) => boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [bootstrapping, setBootstrapping] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const me = await authApi.me()
        if (!cancelled) setUser(toUser(me))
      } catch {
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setBootstrapping(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const dto = await authApi.login(email, password)
    setUser(toUser(dto))
  }, [])

  const register = useCallback(
    async (payload: {
      email: string
      password: string
      name: string
      department: string
    }) => {
      const dto = await authApi.register(payload)
      setUser(toUser(dto))
    },
    [],
  )

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      setUser(null)
    }
  }, [])

  const changePassword = useCallback(async (current: string, next: string) => {
    await authApi.changePassword(current, next)
    setUser(null)
  }, [])

  const hasPermission = useCallback(
    (permission?: Permission) => {
      if (!permission) return true
      if (!user) return false
      return user.permissions.includes(permission)
    },
    [user],
  )

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      bootstrapping,
      login,
      register,
      logout,
      changePassword,
      hasPermission,
    }),
    [user, bootstrapping, login, register, logout, changePassword, hasPermission],
  )

  return createElement(AuthContext.Provider, { value }, children)
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) return err.message
  if (err instanceof Error) return err.message
  return fallback
}
