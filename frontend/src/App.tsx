/**
 * Main App Component
 * AD-1: File upload with drag and drop
 * AD-2: Question flow
 * AD-3: Advanced validation with suggestions
 * AD-5: OAuth2 Dropbox authentication guard
 * AD-7: Status messages (US-09)
 *
 * Refactored to use interfaces.md architecture:
 * - AppShell layout
 * - ChatHeader
 * - Modern UI components
 * - Drag and drop file upload
 * - Conversation-style interface
 */
import React, { useState, useEffect } from 'react'
import { QuestionFlow } from './components/QuestionFlow'
import { LoginScreen } from './components/LoginScreen'
import { StatusMessage, MessageType } from './components/StatusMessage'
import { AppShell } from './components/AppShell'
import { ChatHeader } from './components/ChatHeader'
import { FileUploadWidget } from './components/FileUploadWidget'
import { FileMetadata } from './types/api'
import { UserProvider } from './contexts/UserContext'
import { NotificationProvider } from './contexts/NotificationContext'
import { NotificationContainer } from './components/NotificationContainer'
import './components/DragDropStyles.css'

interface StatusMsg {
  type: MessageType
  message: string
}

function App() {
  const [fileId, setFileId] = useState<string | null>(null)
  const [fileMetadata, setFileMetadata] = useState<FileMetadata | null>(null)
  const [suggestedName, setSuggestedName] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [statusMessage, setStatusMessage] = useState<StatusMsg | null>(null)

  // Check authentication status on mount and after login
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      console.log('Verificando estado de autenticación...')
      const response = await fetch(`http://localhost:8000/auth/status`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache'
        }
      })

      console.log('Respuesta de auth/status:', response.status, response.statusText)
      
      if (response.status === 200) {
        const data = await response.json()
        console.log('Datos de autenticación:', data)
        setIsAuthenticated(data.authenticated)
      } else {
        console.error('Error en auth/status:', response.status, response.statusText)
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      setIsAuthenticated(false)
    }
  }

  const handleLoginSuccess = () => {
    checkAuthStatus()
  }

  const handleFileUploadComplete = (metadata: FileMetadata) => {
    setFileId(metadata.file_id)
    setFileMetadata(metadata)
    setStatusMessage({
      type: 'success',
      message: `Archivo "${metadata.original_name}" cargado correctamente`
    })
  }

  const handleComplete = (name: string) => {
    setSuggestedName(name)
    setStatusMessage({
      type: 'success',
      message: '¡Archivo subido exitosamente a Dropbox!'
    })
  }

  const handleReset = () => {
    setFileId(null)
    setFileMetadata(null)
    setSuggestedName(null)
    setStatusMessage(null)
  }

  const handleCloseMessage = () => {
    setStatusMessage(null)
  }

  // Show loading while checking auth status
  if (isAuthenticated === null) {
    return (
      <AppShell header={<ChatHeader title="🗂️ Dropbox Chatbot Organizer" />}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100%',
          color: 'var(--text-secondary)'
        }}>
          <p>Verificando autenticación...</p>
        </div>
      </AppShell>
    )
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />
  }

  // Show main app if authenticated - Chat AI style
  return (
    <NotificationProvider>
      <UserProvider>
        <NotificationContainer />
        <AppShell
          header={
            <ChatHeader
              title="Dropbox AI Organizer"
              subtitle="Organizador inteligente de archivos"
              showUserInfo={true}
            />
          }
        >
      {/* Chat interface */}
      {!suggestedName ? (
        <div className="chat-container">
          {!fileId ? (
            <div className="welcome-container">
              <h1 className="welcome-title">Bienvenido al Organizador de Archivos</h1>
              <p className="welcome-text">Adjunta un archivo para comenzar la conversación y te ayudaré a organizarlo en tu Dropbox.</p>
              <FileUploadWidget onUploadComplete={handleFileUploadComplete} />
            </div>
          ) : (
            <div className="conversation-container">
              <QuestionFlow
                fileId={fileId}
                fileMetadata={fileMetadata}
                onComplete={handleComplete}
                onCancel={handleReset}
                onError={(msg) => setStatusMessage({ type: 'error', message: msg })}
              />
            </div>
          )}
        </div>
      ) : (
        // Success screen - minimalista
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 'var(--space-6)'
        }}>
          <div style={{
            maxWidth: '600px',
            width: '100%',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '48px',
              marginBottom: 'var(--space-6)'
            }}>
              ✓
            </div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: 500,
              marginBottom: 'var(--space-4)',
              color: 'var(--text-primary)'
            }}>
              Archivo subido correctamente
            </h2>
            <div style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-6)',
              marginBottom: 'var(--space-8)'
            }}>
              <p style={{
                fontSize: '14px',
                color: 'var(--text-tertiary)',
                marginBottom: 'var(--space-2)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Ruta en Dropbox
              </p>
              <p style={{
                fontSize: '16px',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                wordBreak: 'break-all',
                margin: 0
              }}>
                {suggestedName}
              </p>
            </div>
            <button
              onClick={handleReset}
              style={{
                padding: 'var(--space-3) var(--space-8)',
                fontSize: '15px',
                background: 'var(--accent-primary)',
                color: 'var(--text-inverse)',
                border: 'none',
                borderRadius: 'var(--radius-lg)',
                cursor: 'pointer',
                fontWeight: 500,
                transition: 'all 150ms ease-out'
              }}
              onMouseOver={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseOut={(e) => e.currentTarget.style.opacity = '1'}
            >
              Subir nuevo archivo
            </button>
          </div>
        </div>
      )}

      {/* Status messages overlay */}
      {/* Las notificaciones ahora solo se muestran en el panel de notificaciones */}
      </AppShell>
      </UserProvider>
    </NotificationProvider>
  )
}

export default App
