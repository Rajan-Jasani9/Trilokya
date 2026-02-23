import React, { useState, useEffect, useRef } from 'react'
import { FiMoreVertical } from 'react-icons/fi'

const Dropdown = ({ trigger, children, align = 'right' }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [position, setPosition] = useState({ top: 0, right: 0 })
  const dropdownRef = useRef(null)
  const buttonRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      if (buttonRef.current) {
        const rect = buttonRef.current.getBoundingClientRect()
        if (align === 'right') {
          setPosition({ top: rect.bottom + 4, right: window.innerWidth - rect.right })
        } else {
          setPosition({ top: rect.bottom + 4, left: rect.left })
        }
      }
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, align])

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded text-gray-500 hover:text-primary-700 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px] min-w-[44px] flex items-center justify-center transition-colors duration-150"
        aria-label="Actions"
      >
        {trigger || <FiMoreVertical className="h-5 w-5" />}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div
            className="fixed w-48 bg-white rounded-md py-1 z-50 border"
            style={{
              borderColor: '#D9E2E2',
              boxShadow: '0 4px 16px rgba(0,0,0,0.10)',
              ...(align === 'right'
                ? { top: `${position.top}px`, right: `${position.right}px` }
                : { top: `${position.top}px`, left: `${position.left}px` }),
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {children}
          </div>
        </>
      )}
    </div>
  )
}

export const DropdownItem = ({ onClick, children, icon: Icon, danger = false }) => {
  return (
    <button
      onClick={() => onClick()}
      className={`
        w-full text-left px-4 py-2 text-sm flex items-center gap-2
        ${danger
          ? 'text-trl-low hover:bg-red-50'
          : 'text-gray-700 hover:bg-primary-50'
        }
        transition-colors min-h-[44px]
      `}
    >
      {Icon && <Icon className="h-4 w-4 flex-shrink-0" />}
      <span>{children}</span>
    </button>
  )
}

export default Dropdown
