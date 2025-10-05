/**
 * FilePreviewCard Component
 * Muestra información del archivo que se está procesando
 */
import React from 'react'
import './FilePreviewCard.css'

interface FilePreviewCardProps {
  fileName: string
  fileSize?: number
  fileType?: string
  onRemove?: () => void
}

export function FilePreviewCard({ fileName, fileSize, fileType, onRemove }: FilePreviewCardProps) {
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return 'Tamaño desconocido'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getFileIcon = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf':
        return '📄'
      case 'doc':
      case 'docx':
        return '📝'
      case 'xls':
      case 'xlsx':
        return '📊'
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️'
      case 'txt':
        return '📃'
      default:
        return '📁'
    }
  }

  return (
    <div className="file-preview-card">
      <div className="file-preview-card__icon">
        {getFileIcon(fileName)}
      </div>
      <div className="file-preview-card__info">
        <p className="file-preview-card__name" title={fileName}>{fileName}</p>
        <div className="file-preview-card__meta">
          {fileSize && <span className="file-preview-card__size">{formatFileSize(fileSize)}</span>}
          {fileType && <span className="file-preview-card__type">{fileType}</span>}
        </div>
      </div>
      <div className="file-preview-card__actions">
        {onRemove ? (
          <button
            onClick={onRemove}
            className="file-preview-card__remove"
            aria-label="Eliminar archivo"
            title="Eliminar archivo"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        ) : (
          <div className="file-preview-card__checkmark">✓</div>
        )}
      </div>
    </div>
  )
}
