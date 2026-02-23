import React, { useEffect } from 'react'
import { FiX } from 'react-icons/fi'

const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className={`
            relative bg-white rounded-md border w-full ${sizeClasses[size]}
            transform transition-all duration-200
            ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}
          `}
          style={{ borderColor: '#D9E2E2', boxShadow: '0 8px 30px rgba(0,0,0,0.12)' }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between px-6 py-4 border-b rounded-t-md"
            style={{ borderColor: '#D9E2E2', backgroundColor: '#f0f6f6' }}
          >
            <h2 className="text-base font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 rounded text-gray-400 hover:text-gray-700 hover:bg-primary-50 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Close"
            >
              <FiX className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">{children}</div>
        </div>
      </div>
    </div>
  )
}

export default Modal
