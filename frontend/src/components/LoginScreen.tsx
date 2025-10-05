/**
 * LoginScreen Component - AD-5
 * Dropbox OAuth2 login screen
 * Redesigned with modern minimalist aesthetic
 */
import React from 'react'
import './LoginScreen.css'

interface LoginScreenProps {
  onLoginSuccess: () => void
}

export function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const handleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = 'http://localhost:8000/auth/dropbox/login'
  }

  return (
    <div className="login-screen">
      <div className="login-screen__background">
        <div className="login-screen__gradient"></div>
      </div>

      <div className="login-screen__content">
        {/* Header */}
        <div className="login-screen__header">
          <div className="login-screen__logo">
            <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
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
          <h1 className="login-screen__title">Dropbox AI Organizer</h1>
          <p className="login-screen__subtitle">Organizador inteligente de archivos</p>
        </div>

        {/* Main card */}
        <div className="login-screen__card">
          <div className="login-screen__card-icon">🔐</div>

          <h2 className="login-screen__card-title">Conecta tu cuenta</h2>

          <p className="login-screen__card-description">
            Necesitas autorizar esta aplicación para organizar y subir archivos a tu Dropbox de forma automática.
          </p>

          <button
            onClick={handleLogin}
            className="login-screen__button"
          >
            <svg width="20" height="20" viewBox="0 0 64 64" fill="none" style={{ marginRight: '12px' }}>
              <path d="M16 8L32 20L16 32L0 20L16 8Z" fill="currentColor"/>
              <path d="M48 8L64 20L48 32L32 20L48 8Z" fill="currentColor"/>
              <path d="M0 36L16 48L32 36L16 24L0 36Z" fill="currentColor"/>
              <path d="M32 36L48 48L64 36L48 24L32 36Z" fill="currentColor"/>
              <path d="M16 52L32 40L48 52L32 64L16 52Z" fill="currentColor"/>
            </svg>
            Conectar con Dropbox
          </button>

          <div className="login-screen__features">
            <div className="login-screen__feature">
              <span className="login-screen__feature-icon">✓</span>
              <span className="login-screen__feature-text">Organización automática</span>
            </div>
            <div className="login-screen__feature">
              <span className="login-screen__feature-icon">✓</span>
              <span className="login-screen__feature-text">Nombres descriptivos</span>
            </div>
            <div className="login-screen__feature">
              <span className="login-screen__feature-icon">✓</span>
              <span className="login-screen__feature-text">Clasificación inteligente</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="login-screen__footer">
          Tus datos están seguros. Solo solicitamos los permisos necesarios.
        </p>
      </div>
    </div>
  )
}
