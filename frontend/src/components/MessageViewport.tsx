/**
 * MessageViewport Component
 * Área de mensajes estilo chat AI (ChatGPT/Claude)
 * Con scroll automático y diseño centrado
 */
import React, { useEffect, useRef } from 'react'
import './MessageViewport.css'

interface MessageViewportProps {
  children: React.ReactNode
}

export function MessageViewport({ children }: MessageViewportProps) {
  const viewportRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll al final cuando hay nuevos mensajes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [children])

  return (
    <div className="message-viewport" ref={viewportRef}>
      <div className="message-viewport__content">
        {children}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
