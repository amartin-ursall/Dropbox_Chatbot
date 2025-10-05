/**
 * AppShell Component
 * Main layout container following interfaces.md architecture
 */
import React from 'react'
import './AppShell.css'

interface AppShellProps {
  children: React.ReactNode
  header?: React.ReactNode
}

export function AppShell({ children, header }: AppShellProps) {
  return (
    <div className="app-shell">
      {header && <div className="app-shell__header">{header}</div>}
      <main className="app-shell__main">
        {children}
      </main>
    </div>
  )
}
