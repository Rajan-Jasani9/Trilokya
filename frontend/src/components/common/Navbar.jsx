import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { FiMenu, FiUser, FiLogOut } from 'react-icons/fi'

const Navbar = ({ onMenuClick }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const goToProfile = () => {
    setUserMenuOpen(false)
    navigate('/app/profile')
  }

  return (
    <nav className="bg-primary-700 border-b border-primary-800">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          {/* Left – hamburger + brand */}
          <div className="flex items-center gap-3">
            <button
              onClick={onMenuClick}
              className="md:hidden p-2 rounded text-primary-200 hover:text-white hover:bg-primary-600 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Toggle menu"
            >
              <FiMenu className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 bg-white/15 rounded flex items-center justify-center">
                <span className="text-white font-bold text-xs tracking-wide">TRI</span>
              </div>
              <h1 className="text-base font-semibold text-white hidden sm:block tracking-wide">
                Trilokya
              </h1>
            </div>
          </div>

          {/* Right – user menu */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded text-primary-100 hover:bg-primary-600 transition-colors min-h-[44px]"
            >
              <div className="h-7 w-7 bg-white/15 rounded flex items-center justify-center">
                <FiUser className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="hidden sm:block text-sm font-medium text-white">
                {user?.full_name || user?.username}
              </span>
            </button>

            {userMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setUserMenuOpen(false)}
                />
                <div className="absolute right-0 mt-1.5 w-56 bg-white rounded-md border border-shell-border z-50"
                  style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.10)' }}
                >
                  <div className="px-4 py-3 border-b border-shell-border">
                    <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{user?.email}</p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={goToProfile}
                      className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-primary-50 flex items-center gap-2 transition-colors min-h-[44px]"
                    >
                      <FiUser className="h-4 w-4 text-primary-700" />
                      <span>Profile</span>
                    </button>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-primary-50 flex items-center gap-2 transition-colors min-h-[44px]"
                    >
                      <FiLogOut className="h-4 w-4 text-primary-700" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
