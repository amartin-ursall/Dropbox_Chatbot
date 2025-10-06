/**
 * UserInfo Component
 * Muestra información del usuario de Dropbox usando UserContext
 */
import React, { useState, useRef, useEffect } from 'react'
import { useUser } from '../contexts/UserContext'
import './UserInfo.css'

const API_BASE_URL = 'http://localhost:8000'

export function UserInfo() {
  const { userInfo, isLoading, authError, refreshUserInfo } = useUser()
  const [isOpen, setIsOpen] = useState(false)
  const [isClosing, setIsClosing] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  const closeWithAnimation = () => {
    setIsClosing(true)
    setTimeout(() => {
      setIsOpen(false)
      setIsClosing(false)
    }, 200) // Duración de la animación
  }

  // Cerrar el panel al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node) && isOpen && !isClosing) {
        closeWithAnimation()
      }
    }

    if (isOpen && !isClosing) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, isClosing])

  const handleRefresh = () => {
    refreshUserInfo()
  }
  
  const handleDropboxLogin = () => {
    // Usar el mismo endpoint que LoginScreen.tsx
    window.location.href = `${API_BASE_URL}/auth/dropbox/login`
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const getUsagePercentage = (): number => {
    if (!userInfo || userInfo.allocated_space === 0) return 0
    return Math.round((userInfo.used_space / userInfo.allocated_space) * 100)
  }

  const getRemainingSpace = (): string => {
    if (!userInfo) return '0 Bytes'
    return formatBytes(userInfo.allocated_space - userInfo.used_space)
  }

  return (
    <div className="user-info" ref={panelRef}>
      <button
        className="user-info__trigger"
        onClick={() => {
          if (isOpen && !isClosing) {
            closeWithAnimation()
          } else if (!isOpen && !isClosing) {
            setIsOpen(true)
          }
        }}
        aria-label="Información del usuario"
      >
        <div className="user-info__avatar">
          {userInfo?.profile_photo_url ? (
            <img
              src={userInfo.profile_photo_url}
              alt={userInfo.name}
              className="user-info__avatar-img"
            />
          ) : (
            userInfo?.name?.charAt(0).toUpperCase() || '👤'
          )}
        </div>
      </button>

      {(isOpen || isClosing) && (
        <>
          <div className={`user-info__panel ${isClosing ? 'user-info__panel--closing' : ''}`}>
            {isLoading ? (
              <div className="user-info__loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Cargando información...</p>
              </div>
            ) : authError ? (
              <div className="user-info__auth-error">
                <p>Necesitas iniciar sesión con Dropbox para ver tu información.</p>
                <button 
                  className="user-info__login-button" 
                  onClick={handleDropboxLogin}
                >
                  Iniciar sesión con Dropbox
                </button>
              </div>
            ) : userInfo ? (
              <>
                <div className="user-info__header">
                  <div className="user-info__avatar user-info__avatar--large">
                    {userInfo.profile_photo_url ? (
                      <img
                        src={userInfo.profile_photo_url}
                        alt={userInfo.name}
                        className="user-info__avatar-img"
                      />
                    ) : (
                      userInfo.name.charAt(0).toUpperCase()
                    )}
                  </div>
                  <div className="user-info__details">
                    <h3 className="user-info__name">{userInfo.name}</h3>
                    <p className="user-info__email">{userInfo.email}</p>
                    <span className="user-info__badge">{userInfo.account_type}</span>
                  </div>
                </div>

                <div className="user-info__storage">
                  <div className="user-info__storage-header">
                    <span className="user-info__storage-label">Almacenamiento</span>
                    <span className="user-info__storage-percentage">{getUsagePercentage()}%</span>
                  </div>

                  <div className="user-info__storage-bar">
                    <div
                      className="user-info__storage-fill"
                      style={{ width: `${getUsagePercentage()}%` }}
                    />
                  </div>

                  <div className="user-info__storage-stats">
                    <div className="user-info__stat">
                      <span className="user-info__stat-label">Usado</span>
                      <span className="user-info__stat-value">{formatBytes(userInfo.used_space)}</span>
                    </div>
                    <div className="user-info__stat">
                      <span className="user-info__stat-label">Disponible</span>
                      <span className="user-info__stat-value">{getRemainingSpace()}</span>
                    </div>
                    <div className="user-info__stat">
                      <span className="user-info__stat-label">Total</span>
                      <span className="user-info__stat-value">{formatBytes(userInfo.allocated_space)}</span>
                    </div>
                  </div>
                </div>

                <div className="user-info__actions">
                  <button
                    className="user-info__logout"
                    onClick={async () => {
                      try {
                        await fetch('http://localhost:8000/auth/logout', { method: 'POST' })
                        window.location.reload()
                      } catch (error) {
                        console.error('Error logging out:', error)
                      }
                    }}
                  >
                    🚪 Cerrar sesión
                  </button>
                  <button
                    className="user-info__close"
                    onClick={() => setIsOpen(false)}
                  >
                    Cerrar
                  </button>
                </div>
              </>
            ) : (
              <div className="user-info__error">
                <p>Error al cargar información del usuario</p>
                <button onClick={handleRefresh}>Reintentar</button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
