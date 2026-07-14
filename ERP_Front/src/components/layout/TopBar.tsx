import { Link, useNavigate } from 'react-router-dom'
import {
  Bell,
  CircleHelp,
  LogOut,
  Menu,
  KeyRound,
} from 'lucide-react'
import { useAuth } from '@/auth/AuthContext'
import { IconButton } from '@/components/ui/IconButton'
import { SearchField } from '@/components/ui/SearchField'
import { useState, useRef, useEffect } from 'react'
import logo from '@/assets/Logo_MEGACELL_shadow_A_En.png'

export function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const initials = user?.name?.slice(0, 1) ?? '?'

  return (
    <header className="topbar">
      <IconButton label="메뉴 열기" className="menu-btn" onClick={onMenuClick}>
        <Menu size={20} />
      </IconButton>

      <Link to="/" className="topbar__brand">
        <img src={logo} alt="MegaCell Co., Ltd." className="topbar__logo-img" />
        <span className="env-badge">DEV</span>
      </Link>

      <div className="topbar__search">
        <SearchField
          label="전역 검색"
          placeholder="업무번호, 고객, 제품 검색"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              const value = (e.target as HTMLInputElement).value
              if (value) navigate(`/sales/orders?q=${encodeURIComponent(value)}`)
            }
          }}
        />
      </div>

      <div className="topbar__actions">
        <IconButton label="알림">
          <Bell size={18} />
        </IconButton>
        <IconButton label="도움말" onClick={() => navigate('/help')}>
          <CircleHelp size={18} />
        </IconButton>

        <div ref={menuRef} style={{ position: 'relative' }}>
          <button
            type="button"
            className="user-menu"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
          >
            <span className="user-avatar">{initials}</span>
            <span className="user-meta">
              <div className="user-meta__name">{user?.name}</div>
              <div className="user-meta__role">{user?.department}</div>
            </span>
          </button>
          {menuOpen && (
            <div
              role="menu"
              style={{
                position: 'absolute',
                right: 0,
                top: 'calc(100% + 4px)',
                width: 200,
                background: 'var(--color-neutral-0)',
                border: '1px solid var(--color-neutral-200)',
                borderRadius: 8,
                boxShadow: 'var(--shadow-md)',
                padding: 4,
                zIndex: 100,
              }}
            >
              <button
                type="button"
                role="menuitem"
                className="nav-item"
                onClick={() => {
                  setMenuOpen(false)
                  navigate('/account/password')
                }}
              >
                <KeyRound size={16} />
                비밀번호 변경
              </button>
              <button
                type="button"
                role="menuitem"
                className="nav-item"
                onClick={() => {
                  void (async () => {
                    setMenuOpen(false)
                    await logout()
                    navigate('/login')
                  })()
                }}
              >
                <LogOut size={16} />
                로그아웃
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
