import React from 'react'

const LoadingSpinner = ({ size = 'md', fullScreen = false }) => {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-[3px]',
    lg: 'h-12 w-12 border-4',
  }

  const spinner = (
    <div className="flex items-center justify-center">
      <div
        className={`
          ${sizeClasses[size]}
          border-primary-100 border-t-primary-600
          rounded-full animate-spin
        `}
      />
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-shell-background/80 z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}

export default LoadingSpinner
