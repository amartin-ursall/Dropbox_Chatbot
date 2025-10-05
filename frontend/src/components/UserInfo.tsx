/**
 * UserInfo Component
 * Muestra información del usuario de Dropbox
 */
import React, { useState, useEffect } from 'react'
import './UserInfo.css'

interface DropboxAccountInfo {
  name: string
  email: string
  used_space: number
  allocated_space: number
  account_type: string
  profile_photo_url?: string
}

interface CachedUserInfo {
  data: DropboxAccountInfo
  timestamp: number
}

const API_BASE_URL = 'http://localhost:8000'
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutos en milisegundos
const CACHE_KEY = 'dropbox_user_info_cache'

export function UserInfo() {
  const [userInfo, setUserInfo] = useState<DropboxAccountInfo | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [authError, setAuthError] = useState(false)

  // Cargar datos del caché al montar el componente
  useEffect(() => {
    const cachedData = localStorage.getItem(CACHE_KEY)
    if (cachedData) {
      try {
        const cached: CachedUserInfo = JSON.parse(cachedData)
        const now = Date.now()

        // Si el caché es válido, cargar los datos
        if (now - cached.timestamp < CACHE_DURATION) {
          setUserInfo(cached.data)
        }
      } catch (error) {
        console.error('Error loading cache:', error)
      }
    }
  }, [])

  useEffect(() => {
    if (isOpen) {
      fetchUserInfo()
    }
  }, [isOpen])

  const fetchUserInfo = async () => {
    try {
      setIsLoading(true)
      setAuthError(false)

      // Intentar cargar desde caché primero
      const cachedData = localStorage.getItem(CACHE_KEY)
      if (cachedData) {
        const cached: CachedUserInfo = JSON.parse(cachedData)
        const now = Date.now()

        // Si el caché es válido (menos de 5 minutos), usarlo
        if (now - cached.timestamp < CACHE_DURATION) {
          console.log('Usando datos del caché')
          setUserInfo(cached.data)
          setIsLoading(false)
          return
        }
      }

      console.log('Iniciando petición a /api/user/info')
      const response = await fetch(`${API_BASE_URL}/api/user/info`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache'
        }
      })

      console.log('Respuesta recibida:', response.status, response.statusText)

      if (response.status === 200) {
        const data = await response.json()
        console.log('Datos reales recibidos:', data)
        setUserInfo(data)

        // Guardar en caché
        const cacheData: CachedUserInfo = {
          data,
          timestamp: Date.now()
        }
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
      } else if (response.status === 401) {
        setAuthError(true)
      } else {
        console.error(`Error fetching user info: ${response.status} - ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error en la petición:', error)
      setAuthError(true)
    } finally {
      setIsLoading(false)
    }
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
    <div className="user-info">
      <button
        className="user-info__trigger"
        onClick={() => setIsOpen(!isOpen)}
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

      {isOpen && (
        <>
          <div className="user-info__panel">
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
                        // Limpiar caché al cerrar sesión
                        localStorage.removeItem(CACHE_KEY)
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
                <button onClick={fetchUserInfo}>Reintentar</button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
