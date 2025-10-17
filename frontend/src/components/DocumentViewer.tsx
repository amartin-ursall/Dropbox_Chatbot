import React, { useState, useEffect } from 'react';
import './DocumentViewer.css';

interface DocumentViewerProps {
  fileId: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://192.168.0.98:8000';

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  fileId,
  fileName,
  fileType,
  fileSize,
  onConfirm,
  onCancel,
  isLoading = false
}) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPreview();
  }, [fileId]);

  const loadPreview = async () => {
    try {
      setIsLoadingPreview(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/file-preview/${fileId}`);

      if (!response.ok) {
        throw new Error('No se pudo cargar la vista previa');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (err) {
      console.error('Error loading preview:', err);
      setError('No se pudo cargar la vista previa');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileIcon = (): string => {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('image')) return '🖼️';
    if (fileType.includes('word') || fileType.includes('document')) return '📝';
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '📊';
    return '📎';
  };

  const isPDF = fileType.includes('pdf');
  const isImage = fileType.includes('image');

  return (
    <div className="document-viewer">
      {/* Preview del documento */}
      <div className="preview-container">
        {isLoadingPreview && (
          <div className="preview-loading">
            <div className="spinner"></div>
            <p>Cargando vista previa...</p>
          </div>
        )}

        {error && (
          <div className="preview-error">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
          </div>
        )}

        {!isLoadingPreview && !error && previewUrl && (
          <div className="preview-content">
            {/* Always show as image (for PDFs, backend returns thumbnail of first page) */}
            {isImage || isPDF ? (
              <img
                src={previewUrl}
                alt={fileName}
                className="preview-image"
              />
            ) : (
              <div className="preview-placeholder">
                <div className="placeholder-icon">{getFileIcon()}</div>
                <p className="placeholder-text">{fileName}</p>
                <p className="placeholder-hint">Vista previa no disponible</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Info del documento */}
      <div className="document-info-bar">
        <div className="info-item">
          <span className="info-icon">{getFileIcon()}</span>
          <span className="info-text">{fileName}</span>
        </div>
        <div className="info-item">
          <span className="info-label">{formatFileSize(fileSize)}</span>
        </div>
      </div>

      {/* Progress indicator when analyzing */}
      {isLoading && (
        <div className="analysis-progress">
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
          <p className="progress-text">Analizando documento con IA...</p>
        </div>
      )}

      {/* Botones de acción */}
      <div className="viewer-actions">
        <button
          className="btn-cancel"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancelar
        </button>
        <button
          className="btn-confirm"
          onClick={onConfirm}
          disabled={isLoading || isLoadingPreview}
        >
          {isLoading ? (
            <>
              <div className="btn-spinner"></div>
              Analizando...
            </>
          ) : (
            'Confirmar y Analizar'
          )}
        </button>
      </div>
    </div>
  );
};

export default DocumentViewer;
