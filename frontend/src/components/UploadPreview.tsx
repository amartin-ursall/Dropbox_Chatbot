/**
 * UploadPreview Component - AD-4
 * Shows preview of suggested filename and Dropbox path
 * Allows user to confirm or cancel upload
 * Redesigned to match chat aesthetic
 */
import React from 'react'
import { MessageBubble } from './MessageBubble'
import { MessageViewport } from './MessageViewport'
import './UploadPreview.css'

export interface UploadPreviewProps {
  suggestedName: string
  suggestedPath: string
  onConfirm: () => void
  onCancel: () => void
  onEdit?: () => void  // AD-9
  isUploading?: boolean
}

export function UploadPreview({
  suggestedName,
  suggestedPath,
  onConfirm,
  onCancel,
  onEdit,
  isUploading = false
}: UploadPreviewProps) {
  return (
    <>
      <MessageViewport>
        {/* Assistant message with preview */}
        <MessageBubble
          role="assistant"
          content={
            <div>
              <p style={{ marginTop: 0 }}>
                ✅ ¡Perfecto! He analizado tu archivo y generado un nombre descriptivo.
              </p>
              <p style={{ marginBottom: 0 }}>
                Revisa la información y confirma para subir a Dropbox:
              </p>
            </div>
          }
        />

        {/* Preview card */}
        <div className="upload-preview-card">
          <div className="upload-preview-card__section">
            <div className="upload-preview-card__label">
              <span className="upload-preview-card__icon">📄</span>
              Nombre del archivo
            </div>
            <div className="upload-preview-card__value">{suggestedName}</div>
          </div>

          <div className="upload-preview-card__divider"></div>

          <div className="upload-preview-card__section">
            <div className="upload-preview-card__label">
              <span className="upload-preview-card__icon">📁</span>
              Carpeta de destino
            </div>
            <div className="upload-preview-card__value">{suggestedPath}</div>
          </div>

          <div className="upload-preview-card__actions">
            <button
              onClick={onConfirm}
              className="upload-preview-card__button upload-preview-card__button--primary"
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <div className="typing-indicator typing-indicator--small">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Subiendo...
                </>
              ) : (
                <>✓ Confirmar y subir</>
              )}
            </button>

            {onEdit && (
              <button
                onClick={onEdit}
                className="upload-preview-card__button upload-preview-card__button--secondary"
                disabled={isUploading}
              >
                ✏️ Editar respuestas
              </button>
            )}

            <button
              onClick={onCancel}
              className="upload-preview-card__button upload-preview-card__button--tertiary"
              disabled={isUploading}
            >
              ✕ Cancelar
            </button>
          </div>
        </div>
      </MessageViewport>
    </>
  )
}
