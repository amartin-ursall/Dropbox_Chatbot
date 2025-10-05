/**
 * StatusMessage Component - AD-7
 * Displays status messages (success, error, info) to the user
 * US-09: Mensajes de estado en el chat
 */
import React from 'react'

export type MessageType = 'success' | 'error' | 'info' | 'warning'

export interface StatusMessageProps {
  type: MessageType
  message: string
  onClose?: () => void
}

export function StatusMessage({ type, message, onClose }: StatusMessageProps) {
  const getStyles = () => {
    const baseStyles = {
      padding: '1rem',
      borderRadius: '8px',
      marginBottom: '1rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      animation: 'fadeIn 0.3s ease-in'
    }

    switch (type) {
      case 'success':
        return {
          ...baseStyles,
          background: 'rgba(74, 222, 128, 0.1)',
          border: '1px solid rgba(74, 222, 128, 0.3)',
          color: '#4ade80'
        }
      case 'error':
        return {
          ...baseStyles,
          background: 'rgba(248, 113, 113, 0.1)',
          border: '1px solid rgba(248, 113, 113, 0.3)',
          color: '#f87171'
        }
      case 'warning':
        return {
          ...baseStyles,
          background: 'rgba(251, 191, 36, 0.1)',
          border: '1px solid rgba(251, 191, 36, 0.3)',
          color: '#fbbf24'
        }
      case 'info':
      default:
        return {
          ...baseStyles,
          background: 'rgba(96, 165, 250, 0.1)',
          border: '1px solid rgba(96, 165, 250, 0.3)',
          color: '#60a5fa'
        }
    }
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✅'
      case 'error':
        return '❌'
      case 'warning':
        return '⚠️'
      case 'info':
      default:
        return 'ℹ️'
    }
  }

  return (
    <div style={getStyles()} className={`status-message status-${type}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span>{getIcon()}</span>
        <span>{message}</span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'inherit',
            cursor: 'pointer',
            fontSize: '1.2rem',
            padding: '0 0.5rem'
          }}
          aria-label="Cerrar mensaje"
        >
          ×
        </button>
      )}
    </div>
  )
}
