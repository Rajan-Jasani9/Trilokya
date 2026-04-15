import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { FiCheckCircle, FiAlertCircle, FiInfo, FiX } from 'react-icons/fi'

const ToastContext = createContext(null)

const TOAST_STYLES = {
  success: {
    container: 'border-green-200 bg-green-50 text-green-800',
    icon: <FiCheckCircle className="h-4 w-4 text-green-600" />,
  },
  error: {
    container: 'border-red-200 bg-red-50 text-red-800',
    icon: <FiAlertCircle className="h-4 w-4 text-red-600" />,
  },
  info: {
    container: 'border-blue-200 bg-blue-50 text-blue-800',
    icon: <FiInfo className="h-4 w-4 text-blue-600" />,
  },
}

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const showToast = useCallback((message, type = 'info', duration = 3500) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`
    const toast = { id, message, type: TOAST_STYLES[type] ? type : 'info' }
    setToasts((prev) => [...prev, toast])
    window.setTimeout(() => removeToast(id), duration)
  }, [removeToast])

  const value = useMemo(() => ({ showToast }), [showToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-[100] space-y-2 w-[min(92vw,360px)]">
        {toasts.map((toast) => {
          const style = TOAST_STYLES[toast.type] || TOAST_STYLES.info
          return (
            <div key={toast.id} className={`rounded-md border shadow-sm px-3 py-2 flex items-start gap-2 ${style.container}`}>
              <div className="pt-0.5">{style.icon}</div>
              <p className="text-sm flex-1">{toast.message}</p>
              <button
                type="button"
                onClick={() => removeToast(toast.id)}
                className="text-gray-500 hover:text-gray-700 transition-colors"
                aria-label="Dismiss notification"
              >
                <FiX className="h-4 w-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
