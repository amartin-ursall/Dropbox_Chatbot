import React from 'react';
import './DocumentPreview.css';

interface DocumentPreviewData {
  summary: string;
  document_type: string;
  confidence: number;
  is_legal_document: boolean;
  pages: number;
  has_tables: boolean;
  has_figures: boolean;
  suggested_workflow: string;
  key_information: {
    partes?: string[];
    jurisdiccion?: string;
    juzgado?: string;
    numero_procedimiento?: string;
    fecha_documento?: string;
    materia?: string;
    cliente?: string;
    fecha?: string;
    importe?: string;
    concepto?: string;
  };
  suggested_answers?: {
    client?: string;
    partes?: string;
    jurisdiccion?: string;
    materia?: string;
    doc_type?: string;
    date?: string;
  };
}

interface DocumentPreviewProps {
  preview: DocumentPreviewData;
  fileName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  preview,
  fileName,
  onConfirm,
  onCancel,
  isLoading = false
}) => {
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return 'Alta';
    if (confidence >= 0.6) return 'Media';
    return 'Baja';
  };

  const formatDocumentType = (type: string): string => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  return (
    <div className="document-preview">
      <div className="preview-header">
        <div className="header-icon">📄</div>
        <h2>Previsualización del Documento</h2>
        <p className="file-name">{fileName}</p>
      </div>

      <div className="preview-content">
        {/* Main Grid Layout - Two Columns */}
        <div className="preview-main-grid">
          {/* Left Column - Summary & Key Info */}
          <div className="preview-left-column">
            {/* Summary Section */}
            <div className="preview-section summary-section">
              <div className="section-header">
                <h3>📝 Resumen</h3>
              </div>
              <p className="summary-text">{preview.summary}</p>
            </div>

            {/* Key Information */}
            {Object.keys(preview.key_information).length > 0 && (
              <div className="preview-section key-info">
                <div className="section-header">
                  <h3>🔑 Información Clave</h3>
                </div>
                <div className="key-info-grid">
                  {preview.key_information.partes && (
                    <div className="key-info-item">
                      <span className="key-label">Partes</span>
                      <span className="key-value">
                        {Array.isArray(preview.key_information.partes)
                          ? preview.key_information.partes.join(' vs ')
                          : preview.key_information.partes}
                      </span>
                    </div>
                  )}

                  {preview.key_information.jurisdiccion && (
                    <div className="key-info-item">
                      <span className="key-label">Jurisdicción</span>
                      <span className="key-value">{preview.key_information.jurisdiccion}</span>
                    </div>
                  )}

                  {preview.key_information.juzgado && (
                    <div className="key-info-item">
                      <span className="key-label">Juzgado</span>
                      <span className="key-value">{preview.key_information.juzgado}</span>
                    </div>
                  )}

                  {preview.key_information.numero_procedimiento && (
                    <div className="key-info-item">
                      <span className="key-label">Nº Procedimiento</span>
                      <span className="key-value">{preview.key_information.numero_procedimiento}</span>
                    </div>
                  )}

                  {preview.key_information.materia && (
                    <div className="key-info-item">
                      <span className="key-label">Materia</span>
                      <span className="key-value">{preview.key_information.materia}</span>
                    </div>
                  )}

                  {preview.key_information.fecha_documento && (
                    <div className="key-info-item">
                      <span className="key-label">Fecha</span>
                      <span className="key-value">{preview.key_information.fecha_documento}</span>
                    </div>
                  )}

                  {preview.key_information.cliente && (
                    <div className="key-info-item">
                      <span className="key-label">Cliente</span>
                      <span className="key-value">{preview.key_information.cliente}</span>
                    </div>
                  )}

                  {preview.key_information.importe && (
                    <div className="key-info-item">
                      <span className="key-label">Importe</span>
                      <span className="key-value">{preview.key_information.importe}</span>
                    </div>
                  )}

                  {preview.key_information.concepto && (
                    <div className="key-info-item">
                      <span className="key-label">Concepto</span>
                      <span className="key-value">{preview.key_information.concepto}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Document Info & Metadata */}
          <div className="preview-right-column">
            {/* Document Info Card */}
            <div className="preview-section document-info-card">
              <div className="section-header">
                <h3>📊 Información del Documento</h3>
              </div>
              <div className="info-list">
                <div className="info-item">
                  <span className="info-label">Tipo de Documento</span>
                  <span className="info-value document-type">
                    {formatDocumentType(preview.document_type)}
                  </span>
                </div>

                <div className="info-item">
                  <span className="info-label">Confianza</span>
                  <div className="confidence-wrapper">
                    <span className={`confidence-badge ${getConfidenceColor(preview.confidence)}`}>
                      {getConfidenceLabel(preview.confidence)}
                    </span>
                    <span className="confidence-percent">{Math.round(preview.confidence * 100)}%</span>
                  </div>
                </div>

                <div className="info-item">
                  <span className="info-label">Páginas</span>
                  <span className="info-value">{preview.pages}</span>
                </div>

                <div className="info-item">
                  <span className="info-label">Flujo Sugerido</span>
                  <span className={`workflow-badge ${preview.suggested_workflow}`}>
                    {preview.suggested_workflow === 'ursall' ? 'URSALL (Legal)' : 'Estándar'}
                  </span>
                </div>
              </div>

              {/* Document Features */}
              {(preview.has_tables || preview.has_figures || preview.is_legal_document) && (
                <div className="document-features">
                  <span className="features-label">Características:</span>
                  <div className="features-badges">
                    {preview.has_tables && (
                      <span className="feature-badge">📊 Tablas</span>
                    )}
                    {preview.has_figures && (
                      <span className="feature-badge">🖼️ Figuras</span>
                    )}
                    {preview.is_legal_document && (
                      <span className="feature-badge legal">⚖️ Legal</span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Confidence Warning */}
            {preview.confidence < 0.6 && (
              <div className="preview-warning">
                <span className="warning-icon">⚠️</span>
                <div className="warning-content">
                  <strong>Confianza Baja</strong>
                  <p>Verifica que el documento sea correcto antes de continuar.</p>
                </div>
              </div>
            )}

            {/* Suggested Answers Preview */}
            {preview.suggested_answers && Object.keys(preview.suggested_answers).length > 0 && (
              <div className="preview-section suggested-answers">
                <div className="section-header">
                  <h3>💡 Respuestas Sugeridas</h3>
                </div>
                <p className="suggestion-hint">
                  El sistema sugiere las siguientes respuestas basándose en el análisis:
                </p>
                <div className="suggestions-list">
                  {Object.entries(preview.suggested_answers)
                    .filter(([_, value]) => value)
                    .map(([key, value]) => (
                      <div key={key} className="suggestion-item">
                        <span className="suggestion-key">{key}</span>
                        <span className="suggestion-value">{value}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="preview-actions">
        <button
          className="btn-cancel"
          onClick={onCancel}
          disabled={isLoading}
        >
          <span className="button-icon">↩️</span>
          <span>Cancelar y Subir Otro</span>
        </button>
        <button
          className="btn-confirm"
          onClick={onConfirm}
          disabled={isLoading}
        >
          <span className="button-icon">✓</span>
          <span>Confirmar y Continuar</span>
        </button>
      </div>

      {isLoading && (
        <div className="preview-loading-overlay">
          <div className="loading-content">
            <div className="spinner"></div>
            <p>Procesando confirmación...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentPreview;
