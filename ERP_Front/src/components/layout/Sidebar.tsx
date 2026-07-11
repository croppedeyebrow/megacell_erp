import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { NAV_ITEMS } from '@/navigation/menu'
import { useAuth } from '@/auth/AuthContext'
import { cn } from '@/lib/cn'

export function Sidebar({ open, onNavigate }: { open?: boolean; onNavigate?: () => void }) {
  const { hasPermission } = useAuth()
  const location = useLocation()
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const visible = NAV_ITEMS.filter((item) => hasPermission(item.permission))

  return (
    <aside className={cn('sidebar', open && 'sidebar--open')} aria-label="주 메뉴">
      <nav>
        {visible.map((item) => {
          const Icon = item.icon
          const children = item.children?.filter((c) => hasPermission(c.permission))
          const hasChildren = !!children && children.length > 0
          const isChildActive = children?.some((c) => location.pathname.startsWith(c.path))
          const isOpen = expanded[item.id] ?? !!isChildActive

          if (!hasChildren && item.path) {
            return (
              <NavLink
                key={item.id}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => cn('nav-item', isActive && 'nav-item--active')}
                onClick={onNavigate}
              >
                <Icon size={18} aria-hidden />
                <span>{item.label}</span>
              </NavLink>
            )
          }

          return (
            <div key={item.id} className="nav-group">
              <button
                type="button"
                className={cn('nav-item', 'nav-item--parent', isChildActive && 'nav-item--active')}
                aria-expanded={isOpen}
                onClick={() =>
                  setExpanded((prev) => ({ ...prev, [item.id]: !isOpen }))
                }
              >
                <Icon size={18} aria-hidden />
                <span style={{ flex: 1 }}>{item.label}</span>
                {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
              {isOpen && (
                <div className="nav-children">
                  {children?.map((child) => (
                    <NavLink
                      key={child.id}
                      to={child.path}
                      className={({ isActive }) =>
                        cn('nav-item', isActive && 'nav-item--active')
                      }
                      onClick={onNavigate}
                    >
                      {child.label}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
