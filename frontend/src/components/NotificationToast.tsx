/**
 * NotificationToast Component
 * Toast notification individual
 */
import React, { useEffect, useState } from 'react'
import type { Notification } from '../contexts/NotificationContext'
import './NotificationToast.css'

interface NotificationToastProps {
  notification: Notification
  onClose: () => void
}

export function NotificationToast({ notification, onClose }: NotificationToastProps) {
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    // Start exit animation before removal
    const timer = setTimeout(() => {
      setIsExiting(true)
      setTimeout(onClose, 300) // Match animation duration
    }, (notification.duration || 5000) - 300)

    return () => clearTimeout(timer)
  }, [notification.duration, onClose])

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return '✓'
      case 'error':
        return '✕'
      case 'warning':
        return '⚠'
      case 'info':
        return 'ℹ'
      default:
        return 'ℹ'
    }
  }

  return (
    <div
      className={`notification-toast notification-toast--${notification.type} ${
        isExiting ? 'notification-toast--exiting' : ''
      }`}
      role="alert"
    >
      <div className="notification-toast__icon">
        {getIcon()}
      </div>
      <div className="notification-toast__content">
        <div className="notification-toast__title">{notification.title}</div>
        {notification.message && (
          <div className="notification-toast__message">{notification.message}</div>
        )}
      </div>
      <button
        className="notification-toast__close"
        onClick={() => {
          setIsExiting(true)
          setTimeout(onClose, 300)
        }}
        aria-label="Cerrar notificación"
      >
        ✕
      </button>
    </div>
  )
}
