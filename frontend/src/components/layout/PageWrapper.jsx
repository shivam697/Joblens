/**
 * PageWrapper — Common layout wrapping sidebar and content area
 * 
 * All authenticated pages are wrapped in this component.
 * Provides consistent layout with navbar, sidebar, and content area.
 */

import { useState } from 'react'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function PageWrapper({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-app">
      <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 p-6 lg:p-8 min-h-[calc(100vh-4rem)] overflow-x-hidden">
          <div className="max-w-7xl mx-auto animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
