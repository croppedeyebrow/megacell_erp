import { useState, type ReactNode } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { cn } from '@/lib/cn'

export function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <div className={cn('app-shell')}>
      <TopBar onMenuClick={() => setDrawerOpen(true)} />
      <Sidebar open={drawerOpen} onNavigate={() => setDrawerOpen(false)} />
      {drawerOpen && (
        <div
          className="drawer-overlay"
          onClick={() => setDrawerOpen(false)}
          aria-hidden
        />
      )}
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

export function Page({
  children,
  narrow,
}: {
  children: ReactNode
  narrow?: boolean
}) {
  return <div className={cn('page', narrow && 'page--narrow')}>{children}</div>
}
