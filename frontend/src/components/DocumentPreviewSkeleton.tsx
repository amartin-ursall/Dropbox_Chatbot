import React from 'react';
import './DocumentPreviewSkeleton.css';

interface DocumentPreviewSkeletonProps {
  fileName: string;
}

const DocumentPreviewSkeleton: React.FC<DocumentPreviewSkeletonProps> = ({ fileName }) => {
  return (
    <div className="document-preview-skeleton">
      <div className="skeleton-header">
        <div className="skeleton-icon">
          <div className="scanning-animation">
            <div className="scan-line"></div>
          </div>
          📄
        </div>
        <h2>Analizando Documento</h2>
        <p className="skeleton-filename">{fileName}</p>
      </div>

      <div className="skeleton-content">
        {/* Progress Bar */}
        <div className="analysis-progress">
          <div className="progress-label">
            <span>Extrayendo información del documento...</span>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar"></div>
          </div>
        </div>

        {/* Analysis Steps */}
        <div className="analysis-steps">
          <div className="analysis-step active">
            <div className="step-icon">
              <div className="pulse-dot"></div>
            </div>
            <span className="step-label">Leyendo documento</span>
          </div>
          <div className="analysis-step">
            <div className="step-icon">
              <div className="pulse-dot"></div>
            </div>
            <span className="step-label">Extrayendo estructura</span>
          </div>
          <div className="analysis-step">
            <div className="step-icon">
              <div className="pulse-dot"></div>
            </div>
            <span className="step-label">Identificando información clave</span>
          </div>
          <div className="analysis-step">
            <div className="step-icon">
              <div className="pulse-dot"></div>
            </div>
            <span className="step-label">Generando resumen</span>
          </div>
        </div>

        {/* Skeleton Cards */}
        <div className="skeleton-cards">
          {/* Summary Skeleton */}
          <div className="skeleton-card">
            <div className="skeleton-card-header">
              <div className="skeleton-bar skeleton-title"></div>
            </div>
            <div className="skeleton-card-body">
              <div className="skeleton-bar skeleton-line"></div>
              <div className="skeleton-bar skeleton-line"></div>
              <div className="skeleton-bar skeleton-line short"></div>
            </div>
          </div>

          {/* Info Grid Skeleton */}
          <div className="skeleton-card">
            <div className="skeleton-grid">
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
            </div>
          </div>

          {/* Key Info Skeleton */}
          <div className="skeleton-card">
            <div className="skeleton-card-header">
              <div className="skeleton-bar skeleton-title"></div>
            </div>
            <div className="skeleton-grid">
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
              <div className="skeleton-grid-item">
                <div className="skeleton-bar skeleton-label"></div>
                <div className="skeleton-bar skeleton-value"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Tips */}
        <div className="loading-tips">
          <p className="tip-label">💡 Consejo:</p>
          <p className="tip-text">
            El análisis puede tardar unos segundos dependiendo del tamaño y complejidad del documento.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DocumentPreviewSkeleton;
