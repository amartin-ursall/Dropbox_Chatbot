/**
 * ChatHeader Component
 * Header for chat interface following interfaces.md design
 */
import React from 'react'
import { UserInfo } from './UserInfo'
import { NotificationIcon } from './NotificationIcon'
import './ChatHeader.css'

interface ChatHeaderProps {
  title: string
  subtitle?: string
  showUserInfo?: boolean
}

export function ChatHeader({ title, subtitle, showUserInfo = false }: ChatHeaderProps) {
  return (
    <div className="chat-header">
      <div className="chat-header__content">
        <div className="chat-header__logo">
          <svg width="24" height="24" viewBox="0 0 64 64" fill="none">
            <path d="M16 8L32 20L16 32L0 20L16 8Z" fill="url(#gradient1)"/>
            <path d="M48 8L64 20L48 32L32 20L48 8Z" fill="url(#gradient1)"/>
            <path d="M0 36L16 48L32 36L16 24L0 36Z" fill="url(#gradient2)"/>
            <path d="M32 36L48 48L64 36L48 24L32 36Z" fill="url(#gradient2)"/>
            <path d="M16 52L32 40L48 52L32 64L16 52Z" fill="url(#gradient3)"/>
            <defs>
              <linearGradient id="gradient1" x1="0" y1="0" x2="64" y2="64">
                <stop offset="0%" stopColor="#0061FF"/>
                <stop offset="100%" stopColor="#0051D5"/>
              </linearGradient>
              <linearGradient id="gradient2" x1="0" y1="0" x2="64" y2="64">
                <stop offset="0%" stopColor="#0051D5"/>
                <stop offset="100%" stopColor="#0041AA"/>
              </linearGradient>
              <linearGradient id="gradient3" x1="0" y1="0" x2="64" y2="64">
                <stop offset="0%" stopColor="#0041AA"/>
                <stop offset="100%" stopColor="#003180"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div className="chat-header__text">
          <h1 className="chat-header__title">{title}</h1>
          {subtitle && <p className="chat-header__subtitle">{subtitle}</p>}
        </div>
      </div>
      {showUserInfo && (
        <div className="chat-header__actions">
          <NotificationIcon />
          <UserInfo />
        </div>
      )}
    </div>
  )
}
