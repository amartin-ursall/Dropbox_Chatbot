/**
 * QuestionFlow Component - AD-2
 * Handles sequential question asking flow
 * Refactored to use validators utility
 *
 * Flow: idle → asking → validating → completed
 * Shows one question at a time with validation
 *
 * Updated to use interfaces.md design:
 * - MessageBubble for questions and answers
 * - Composer for user input
 * - Modern chat interface
 */
import React, { useState, useEffect } from 'react'
import type { Question, AnswerResponse, SuggestedNameResponse } from '../types/api'
import { validateAnswer } from '../utils/validators'
import { UploadPreview } from './UploadPreview'
import { MessageBubble } from './MessageBubble'
import { Composer } from './Composer'
import { MessageViewport } from './MessageViewport'
import { FilePreviewCard } from './FilePreviewCard'
import type { FileMetadata } from '../types/api'
import { useNotifications } from '../contexts/NotificationContext'
import './TypingIndicator.css'

interface QuestionFlowProps {
  fileId: string | null
  fileMetadata?: FileMetadata | null
  onComplete: (suggestedName: string) => void
  onCancel?: () => void
  onError?: (errorMessage: string) => void
  onFileUpload?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

const API_BASE_URL = 'http://localhost:8000'

export function QuestionFlow({ fileId, fileMetadata, onComplete, onCancel, onError, onFileUpload }: QuestionFlowProps) {
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [validationError, setValidationError] = useState('')
  const [apiError, setApiError] = useState('')
  const [suggestion, setSuggestion] = useState<string | null>(null)  // AD-3
  const [isLoading, setIsLoading] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [suggestedName, setSuggestedName] = useState('')
  const [suggestedPath, setSuggestedPath] = useState('')  // AD-4
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [questionHistory, setQuestionHistory] = useState<Question[]>([])  // AD-9: Track question history
  const { showSuccess, showError } = useNotifications()

  // Start question flow when file is uploaded
  useEffect(() => {
    if (fileId) {
      startQuestions()
    }
  }, [fileId])

  const startQuestions = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/questions/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_id: fileId })
      })

      if (!response.ok) {
        const error = await response.json()
        setApiError(error.detail || 'Error al iniciar preguntas')
        return
      }

      const question: Question = await response.json()
      setCurrentQuestion(question)
    } catch (error) {
      setApiError('Error de conexión. Verifica que el servidor esté activo.')
    } finally {
      setIsLoading(false)
    }
  }

  const validateInput = (value: string): boolean => {
    if (!currentQuestion) return false

    // Reset errors
    setValidationError('')

    // Use refactored validator
    const result = validateAnswer(value, currentQuestion)
    if (!result.isValid) {
      setValidationError(result.error || 'Respuesta inválida')
      return false
    }

    return true
  }

  const handleSubmit = async (userAnswer: string) => {
    if (!currentQuestion) return

    // Validate before sending to backend
    const result = validateAnswer(userAnswer, currentQuestion)
    if (!result.isValid) {
      setValidationError(result.error || 'Respuesta inválida')
      return
    }

    try {
      setIsLoading(true)
      setValidationError('')

      // Submit answer
      const response = await fetch(`${API_BASE_URL}/api/questions/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          question_id: currentQuestion.question_id,
          answer: userAnswer.trim()
        })
      })

      if (!response.ok) {
        const error = await response.json()
        // AD-3: Handle error with suggestion
        if (error.detail && typeof error.detail === 'object' && 'suggestion' in error.detail) {
          setApiError(error.detail.detail)
          setSuggestion(error.detail.suggestion)
        } else {
          setApiError(error.detail || 'Error al enviar respuesta')
          setSuggestion(null)
        }
        return
      }

      // Clear errors and suggestion on success
      setApiError('')
      setSuggestion(null)

      const apiResult: AnswerResponse = await response.json()

      // Store answer
      const newAnswers = {
        ...answers,
        [currentQuestion.question_id]: userAnswer.trim()
      }
      setAnswers(newAnswers)
      setAnswer('')

      if (apiResult.completed) {
        // Generate filename
        await generateFilename(newAnswers)
      } else if (apiResult.next_question) {
        // AD-9: Add current question to history before moving to next
        setQuestionHistory(prev => [...prev, currentQuestion])
        // Move to next question
        setCurrentQuestion(apiResult.next_question)
      }
    } catch (error) {
      setApiError('Error de conexión')
    } finally {
      setIsLoading(false)
    }
  }

  const generateFilename = async (allAnswers: Record<string, string>) => {
    try {
      // Get original extension from fileId (would come from upload response in real app)
      const originalExtension = '.pdf' // Placeholder

      const response = await fetch(`${API_BASE_URL}/api/questions/generate-name`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          answers: allAnswers,
          original_extension: originalExtension
        })
      })

      if (!response.ok) {
        const error = await response.json()
        setApiError(error.detail || 'Error al generar nombre')
        return
      }

      const result: SuggestedNameResponse = await response.json()
      setSuggestedName(result.suggested_name)
      setSuggestedPath(result.suggested_path || '/Documentos/Otros')  // AD-4
      setIsCompleted(true)
      // Don't call onComplete yet - wait for user confirmation (AD-4)
    } catch (error) {
      setApiError('Error al generar nombre de archivo')
    }
  }

  // AD-3: Use suggestion
  const useSuggestion = () => {
    if (suggestion) {
      setAnswer(suggestion)
      setSuggestion(null)
      setValidationError('')
    }
  }

  // AD-6: Confirm upload - upload to Dropbox
  const handleConfirm = async () => {
    try {
      setIsLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/upload-final`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          new_filename: suggestedName,
          dropbox_path: suggestedPath
        })
      })

      if (!response.ok) {
        const error = await response.json()
        const errorMsg = error.detail || 'Error al subir archivo a Dropbox'
        setApiError(errorMsg)
        if (onError) {
          onError(errorMsg)
        }
        return
      }

      const result = await response.json()
      // Call onComplete to notify parent (show success message)
      onComplete(result.dropbox_path)
      showSuccess('Archivo subido a Dropbox', `El archivo se ha subido correctamente a ${result.dropbox_path}`)
    } catch (error) {
      const errorMsg = 'Error de conexión al subir archivo'
      setApiError(errorMsg)
      showError('Error al subir a Dropbox', errorMsg)
      if (onError) {
        onError(errorMsg)
      }
    } finally {
      setIsLoading(false)
    }
  }

  // AD-9: Go back to previous question
  const handleGoBack = () => {
    if (questionHistory.length > 0) {
      const previousQuestion = questionHistory[questionHistory.length - 1]
      const previousAnswer = answers[previousQuestion.question_id] || ''

      // Remove last question from history
      setQuestionHistory(prev => prev.slice(0, -1))

      // Remove current question's answer if exists
      if (currentQuestion) {
        setAnswers(prev => {
          const newAnswers = { ...prev }
          delete newAnswers[currentQuestion.question_id]
          return newAnswers
        })
      }

      // Go back to previous question
      setCurrentQuestion(previousQuestion)
      setAnswer(previousAnswer)
      setValidationError('')
      setApiError('')
      setSuggestion(null)
    }
  }

  // AD-9: Edit answers from preview
  const handleEditAnswers = () => {
    // Go back to first question
    const firstQuestion = questionHistory.length > 0 ? questionHistory[0] : currentQuestion
    if (firstQuestion) {
      setCurrentQuestion(firstQuestion)
      setAnswer(answers[firstQuestion.question_id] || '')
      setQuestionHistory([])
      setIsCompleted(false)
      setValidationError('')
      setApiError('')
      setSuggestion(null)
    }
  }

  // AD-6: Cancel upload
  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
  }

  // Render states
  if (apiError) {
    return (
      <div className="question-flow error">
        <p className="error-message">Error: {apiError}</p>
      </div>
    )
  }

  if (isCompleted) {
    return (
      <UploadPreview
        suggestedName={suggestedName}
        suggestedPath={suggestedPath}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
        onEdit={handleEditAnswers}
        isUploading={isLoading}
      />
    )
  }

  if (!currentQuestion) {
    return (
      <div className="question-flow loading">
        <p>Cargando preguntas...</p>
      </div>
    )
  }

  // Chat AI interface - estilo ChatGPT/Claude
  return (
    <>
      <MessageViewport>
        {/* Welcome message si no hay archivo */}
        {!fileId && (
          <>
            <MessageBubble
              role="assistant"
              content={
                <div>
                  <p style={{ marginTop: 0 }}>
                    👋 ¡Hola! Soy tu asistente de organización de archivos para Dropbox.
                  </p>
                  <p>
                    Sube un archivo y te ayudaré a organizarlo con un nombre descriptivo y ubicarlo en la carpeta correcta.
                  </p>
                  <p style={{ marginBottom: 0 }}>
                    <strong>Archivos compatibles:</strong> PDF, DOCX, XLSX, JPG, PNG, TXT (máx. 50MB)
                  </p>
                </div>
              }
            />
            {onFileUpload && (
              <div style={{
                padding: 'var(--space-6)',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                border: '2px dashed var(--border-medium)',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 200ms ease-out'
              }}
              onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent-muted)'}
              onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-medium)'}
              >
                <input
                  type="file"
                  onChange={onFileUpload}
                  accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png,.txt"
                  style={{ display: 'none' }}
                  id="file-upload-input"
                />
                <label htmlFor="file-upload-input" style={{ cursor: 'pointer', display: 'block' }}>
                  <div style={{ fontSize: '32px', marginBottom: 'var(--space-3)' }}>📁</div>
                  <p style={{ margin: 0, color: 'var(--text-primary)', fontWeight: 500 }}>
                    Haz clic para seleccionar un archivo
                  </p>
                  <p style={{ margin: 'var(--space-2) 0 0 0', fontSize: '14px', color: 'var(--text-tertiary)' }}>
                    o arrastra y suelta aquí
                  </p>
                </label>
              </div>
            )}
          </>
        )}

        {/* Vista previa del archivo subido */}
        {fileId && fileMetadata && (
          <>
            <MessageBubble
              role="user"
              content={
                <FilePreviewCard
                  fileName={fileMetadata.original_name}
                  fileSize={fileMetadata.file_size || fileMetadata.size}
                  fileType={fileMetadata.mime_type}
                  onRemove={!currentQuestion && !isLoading ? onCancel : undefined}
                />
              }
            />
            {!currentQuestion && !isLoading && (
              <MessageBubble
                role="assistant"
                content="📄 Perfecto, archivo recibido. Te haré algunas preguntas para organizarlo correctamente en tu Dropbox..."
              />
            )}
          </>
        )}

        {/* Historial de preguntas y respuestas */}
        {questionHistory.map((q) => (
          <React.Fragment key={q.question_id}>
            <MessageBubble role="assistant" content={q.question_text} />
            {answers[q.question_id] && (
              <MessageBubble role="user" content={answers[q.question_id]} />
            )}
          </React.Fragment>
        ))}

        {/* Pregunta actual */}
        {currentQuestion && (
          <MessageBubble
            role="assistant"
            content={currentQuestion.question_text}
          />
        )}

        {/* Errores de validación */}
        {validationError && (
          <MessageBubble
            role="system"
            content={`⚠️ ${validationError}`}
          />
        )}

        {/* Errores de API */}
        {apiError && (
          <MessageBubble
            role="system"
            content={`❌ ${apiError}`}
          />
        )}

        {/* Sugerencias - estilo AI */}
        {suggestion && (
          <div style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-5)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-4)',
            maxWidth: '600px'
          }}>
            <div style={{ flex: 1 }}>
              <p style={{
                margin: 0,
                color: 'var(--text-secondary)',
                fontSize: '14px',
                marginBottom: 'var(--space-2)'
              }}>
                💡 Sugerencia
              </p>
              <p style={{
                margin: 0,
                color: 'var(--text-primary)',
                fontSize: '15px',
                fontWeight: 500
              }}>
                {suggestion}
              </p>
            </div>
            <button
              type="button"
              onClick={useSuggestion}
              style={{
                padding: 'var(--space-2) var(--space-4)',
                background: 'var(--accent-primary)',
                color: 'var(--text-inverse)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
                whiteSpace: 'nowrap'
              }}
            >
              Usar
            </button>
          </div>
        )}

        {/* Indicador de carga */}
        {isLoading && (
          <MessageBubble
            role="assistant"
            content={
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span style={{ color: 'var(--text-tertiary)' }}>Procesando...</span>
              </div>
            }
          />
        )}

        {/* Botón de atrás - dentro del viewport para que sea scrolleable */}
        {questionHistory.length > 0 && currentQuestion && !isCompleted && (
          <div style={{
            padding: 'var(--space-4) 0',
            display: 'flex',
            justifyContent: 'center'
          }}>
            <button
              type="button"
              onClick={handleGoBack}
              disabled={isLoading}
              style={{
                padding: 'var(--space-3) var(--space-5)',
                fontSize: '14px',
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.5 : 1,
                fontWeight: 500,
                transition: 'all 200ms ease'
              }}
              onMouseOver={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'
                  e.currentTarget.style.borderColor = 'var(--border-strong)'
                }
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'
                e.currentTarget.style.borderColor = 'var(--border-medium)'
              }}
            >
              ← Pregunta anterior
            </button>
          </div>
        )}
      </MessageViewport>

      {/* Input area - solo mostrar si hay pregunta activa */}
      {currentQuestion && !isCompleted && (
        <Composer
          onSubmit={handleSubmit}
          placeholder={currentQuestion.required ? 'Escribe tu respuesta...' : 'Escribe tu respuesta (opcional)...'}
          disabled={isLoading}
        />
      )}
    </>
  )
}
