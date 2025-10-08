/**
 * Composer Component
 * Message input component following interfaces.md design
 * Features:
 * - Auto-grow textarea (min 72px, max 240px)
 * - Submit on Enter, new line on Shift+Enter
 * - Disabled state during loading
 */
import React, { useState, useRef, useEffect } from 'react'
import './Composer.css'

interface ComposerProps {
  onSubmit: (message: string) => void
  placeholder?: string
  disabled?: boolean
}

export function Composer({
  onSubmit,
  placeholder = 'Escribe tu respuesta...',
  disabled = false
}: ComposerProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const scrollHeight = textareaRef.current.scrollHeight
      // Min 36px, Max 160px
      const height = Math.min(Math.max(scrollHeight, 36), 160)
      textareaRef.current.style.height = `${height}px`
    }
  }, [message])
  
  // Mantener el foco en el textarea
  useEffect(() => {
    // Pequeño retraso para asegurar que el DOM esté listo
    const focusTimeout = setTimeout(() => {
      if (textareaRef.current && !disabled) {
        textareaRef.current.focus()
      }
    }, 100)
    
    return () => clearTimeout(focusTimeout)
  }, [disabled])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedMessage = message.trim()
    if (trimmedMessage && !disabled) {
      onSubmit(trimmedMessage)
      setMessage('')
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = '36px'
        // Volver a enfocar el textarea después de enviar
        setTimeout(() => {
          if (textareaRef.current) {
            textareaRef.current.focus()
          }
        }, 10)
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <div className="composer__input-wrapper">
        <textarea
          ref={textareaRef}
          className="composer__textarea"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          aria-label="Mensaje"
          autoFocus
        />
        <button
          type="submit"
          className="composer__send-button"
          disabled={!message.trim() || disabled}
          aria-label="Enviar mensaje"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 10L18 2L10 18L8 11L2 10Z" />
          </svg>
        </button>
      </div>
    </form>
  )
}
