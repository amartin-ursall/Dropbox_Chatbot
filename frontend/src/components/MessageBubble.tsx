/**
 * MessageBubble Component
 * Chat message bubble following interfaces.md design
 * Supports user, assistant, and system messages
 */
import React from 'react'
import { useUser } from '../contexts/UserContext'
import './MessageBubble.css'

export type MessageRole = 'user' | 'assistant' | 'system'

interface MessageBubbleProps {
  role: MessageRole
  content: React.ReactNode
  timestamp?: string
}

export function MessageBubble({ role, content, timestamp }: MessageBubbleProps) {
  const { userInfo } = useUser()

  return (
    <div className={`message-bubble message-bubble--${role}`}>
      {role === 'user' && (
        <div className="message-bubble__avatar">
          {userInfo?.profile_photo_url ? (
            <img
              src={userInfo.profile_photo_url}
              alt={userInfo.name}
              className="message-bubble__avatar-img"
            />
          ) : (
            <div className="message-bubble__avatar-placeholder">
              {userInfo?.name?.charAt(0).toUpperCase() || '👤'}
            </div>
          )}
        </div>
      )}
      <div className="message-bubble__content">
        {content}
      </div>
      {timestamp && (
        <div className="message-bubble__timestamp">{timestamp}</div>
      )}
    </div>
  )
}
