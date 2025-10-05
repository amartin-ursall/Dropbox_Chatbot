/**
 * FileUploadWidget Component
 * Refactored for better maintainability (AD-1)
 * Enhanced with drag and drop functionality
 * Integrated with notification system
 */
import { useState, useRef, useCallback, useEffect } from 'react'
import { FileMetadata, ApiError } from '../types/api'
import { formatFileSize } from '../utils/formatters'
import { API_BASE_URL, ALLOWED_FILE_ACCEPT } from '../config/constants'
import { useNotifications } from '../contexts/NotificationContext'
import './FileUploadWidget.css'

interface FileUploadWidgetProps {
  onUploadComplete: (metadata: FileMetadata) => void
}

export function FileUploadWidget({ onUploadComplete }: FileUploadWidgetProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedMetadata, setUploadedMetadata] = useState<FileMetadata | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropzoneRef = useRef<HTMLDivElement>(null)
  const { showSuccess, showError, showInfo } = useNotifications()

  // Auto-upload file when selected
  useEffect(() => {
    if (selectedFile && !uploading && !uploadSuccess) {
      handleUpload();
    }
  }, [selectedFile]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setUploadSuccess(false)
    }
  }

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const file = files[0]
      setSelectedFile(file)
      setError(null)
      setUploadSuccess(false)
    }
  }, [])

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_BASE_URL}/api/upload-temp`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData: ApiError = await response.json()
        throw new Error(errorData.error || errorData.detail || 'Error al subir archivo')
      }

      const metadata: FileMetadata = await response.json()
      setUploadedMetadata(metadata)
      setUploadSuccess(true)
      onUploadComplete(metadata)
      showSuccess('Archivo subido correctamente', `El archivo ${selectedFile.name} se ha subido correctamente`)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido'
      setError(errorMsg)
      showError('Error al subir archivo', errorMsg)
    } finally {
      setUploading(false)
    }
  }

  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div className="file-upload-widget">
      <div 
        ref={dropzoneRef}
        className={`dropzone ${isDragging ? 'active' : ''} ${selectedFile && !uploadSuccess ? 'has-file' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={!selectedFile || uploadSuccess ? openFileDialog : undefined}
      >
        <input
          ref={fileInputRef}
          id="file-input"
          type="file"
          accept={ALLOWED_FILE_ACCEPT}
          onChange={handleFileSelect}
          disabled={uploading}
          aria-label="Subir archivo"
          style={{ display: 'none' }}
        />
        
        {!selectedFile ? (
          <div className="dropzone-content">
            <div className="dropzone-icon">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 16V8M12 8L8 12M12 8L16 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M3 15V16C3 18.2091 4.79086 20 7 20H17C19.2091 20 21 18.2091 21 16V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2 className="dropzone-title">Adjunta tu archivo</h2>
            <p className="dropzone-text">Arrastra y suelta tu archivo aquí o haz clic para seleccionarlo</p>
            <p className="dropzone-hint">Formatos aceptados: PDF, DOC, DOCX, XLS, XLSX</p>
          </div>
        ) : uploading ? (
          <div className="uploading-indicator">
            <div className="spinner"></div>
            <p>Subiendo archivo...</p>
          </div>
        ) : !uploadSuccess ? (
          <div className="file-preview">
            <div className="file-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="file-info">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{formatFileSize(selectedFile.size)}</p>
              <div>
                <button 
                  className="file-remove-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    setUploadSuccess(false);
                    setUploadedMetadata(null);
                    showInfo('Archivo eliminado', `El archivo ${selectedFile.name} ha sido eliminado`);
                  }}
                  aria-label="Eliminar archivo"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {uploadSuccess && uploadedMetadata && (
        <div className="upload-success">
          <div className="success-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="#22C55E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 4L12 14.01L9 11.01" stroke="#22C55E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <button 
            className="file-remove-button"
            onClick={() => {
              setSelectedFile(null);
              setUploadSuccess(false);
              setUploadedMetadata(null);
              showInfo('Archivo eliminado', `El archivo ${uploadedMetadata.original_name} ha sido eliminado`);
            }}
            aria-label="Eliminar archivo"
            style={{ position: 'absolute', top: '12px', right: '12px' }}
          >
            Eliminar
          </button>
          <div className="chat-message bot">
            <p className="success-title">¡Archivo recibido correctamente!</p>
            <p>He recibido tu archivo "{uploadedMetadata.original_name}". Ahora vamos a organizarlo juntos.</p>
            <button 
              className="file-remove-button"
              onClick={() => {
                setSelectedFile(null);
                setUploadSuccess(false);
                setUploadedMetadata(null);
                showInfo('Archivo eliminado', `El archivo ${uploadedMetadata.original_name} ha sido eliminado`);
              }}
              style={{ marginTop: '10px' }}
            >
              Quitar archivo y volver a la subida
            </button>
          </div>
        </div>
      )}

      {error && (
        <div role="alert" className="upload-error">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}
