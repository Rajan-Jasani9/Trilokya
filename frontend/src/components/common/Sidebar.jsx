import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FiX, FiHome, FiGrid, FiFolder, FiCheckSquare, FiSettings, FiUsers } from 'react-icons/fi'
import { useAuth } from '../../context/AuthContext'

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation()
  const { user } = useAuth()

  const menuItems = [
    { path: '/app/technologies', label: 'Technologies', icon: FiGrid },
    { path: '/app/dashboard', label: 'Dashboard', icon: FiHome },
    { path: '/app/projects', label: 'Projects', icon: FiFolder },
    { path: '/app/ctes', label: 'CTEs', icon: FiCheckSquare },
  ]

  // Add admin-only menus
  const userRoles = user?.roles || []
  const isSuperAdmin = Array.isArray(userRoles)
    ? userRoles.includes('SuperAdmin')
    : userRoles === 'SuperAdmin' || (typeof userRoles === 'string' && userRoles.includes('SuperAdmin'))

  if (isSuperAdmin) {
    menuItems.push({ path: '/app/users', label: 'Users', icon: FiUsers })
    menuItems.push({ path: '/app/admin', label: 'Admin', icon: FiSettings })
  }

  const isActive = (path) => location.pathname.startsWith(path) || location.pathname === path

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed md:static top-0 left-0
          h-screen md:h-full w-60
          bg-white border-r flex-shrink-0
          transform transition-transform duration-200 ease-in-out z-50
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
        style={{ borderColor: '#D9E2E2' }}
      >
        <div className="flex flex-col h-full">
          {/* Mobile close header */}
          <div className="flex items-center justify-between px-4 py-3 border-b md:hidden" style={{ borderColor: '#D9E2E2' }}>
            <span className="text-sm font-semibold text-gray-900">Menu</span>
            <button
              onClick={onClose}
              className="p-2 rounded text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            >
              <FiX className="h-5 w-5" />
            </button>
          </div>

          {/* Nav links */}
          <nav className="flex-1 px-3 py-4 space-y-0.5">
            {menuItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    if (window.innerWidth < 768) onClose()
                  }}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-colors duration-150
                    ${active
                      ? 'bg-primary-50 text-primary-700 border-l-[3px] border-primary-600 pl-[9px]'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-[3px] border-transparent pl-[9px]'
                    }
                  `}
                >
                  <Icon className={`h-[18px] w-[18px] ${active ? 'text-primary-600' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Sidebar footer */}
          <div className="px-4 py-3 border-t text-xs text-gray-400" style={{ borderColor: '#D9E2E2' }}>
            Trilokya v1.0
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
