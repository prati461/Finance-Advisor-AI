import os

# Fix AppLayout.tsx - complete rewrite
applayout_path = 'frontend/src/components/layout/AppLayout.tsx'
applayout_content = """import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'
import { Footer } from './Footer'

export function AppLayout() {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen flex">
      <Sidebar
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
        collapsed={collapsed}
        onCollapse={setCollapsed}
      />
      <div className={'flex-1 flex flex-col transition-all duration-300 ' + (collapsed ? 'lg:ml-20' : 'lg:ml-64')}>
        <Navbar onMenuClick={() => setIsMobileOpen(true)} />
        <main className="flex-1 p-4 lg:p-6 xl:p-8">
          <Outlet />
        </main>
        <Footer />
      </div>
  )
}
"""
with open(applayout_path, 'w', encoding='utf-8') as f:
    f.write(applayout_content)
print('AppLayout.tsx fixed. Open divs:', applayout_content.count('<div'), 'Close divs:', applayout_content.count('</div>'))
