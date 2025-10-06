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
  const [folderStructure, setFolderStructure] = useState<string[]>([])  // URSALL: carpetas a crear
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [questionHistory, setQuestionHistory] = useState<Question[]>([])  // AD-9: Track question history
  const [isGeneratingResponse, setIsGeneratingResponse] = useState(false)  // Estado para simular "generando respuesta"
  const [simulatedResponse, setSimulatedResponse] = useState<string>('')  // Respuesta simulada durante el delay
  const [simulatedResponses, setSimulatedResponses] = useState<Record<string, string>>({})  // Respuestas simuladas guardadas
  const { showSuccess, showError } = useNotifications()

  // Función para generar respuesta simulada basada en la pregunta
  const generateSimulatedResponse = (question: Question, userAnswer: string): string => {
    const questionId = question.question_id
    const questionText = question.question_text
    
    switch (questionId) {
      case 'doc_type':
        return `Pregunta: "${questionText}"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nRespuesta: ${userAnswer}`
      case 'client':
        return `Pregunta: "${questionText}"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nRespuesta: ${userAnswer}`
      case 'date':
        return `Pregunta: "${questionText}"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nRespuesta: ${userAnswer}`
      default:
        return `Pregunta: "${questionText}"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nRespuesta: ${userAnswer}`
    }
  }

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

      // Mostrar inmediatamente la respuesta del usuario
      const newAnswers = {
        ...answers,
        [currentQuestion.question_id]: userAnswer.trim()
      }
      setAnswers(newAnswers)
      setAnswer('')

      // Añadir la pregunta actual al historial
      setQuestionHistory(prev => [...prev, currentQuestion])

      // Generar respuesta simulada y activar estado de "generando respuesta"
      const simResponse = generateSimulatedResponse(currentQuestion, userAnswer.trim())
      setSimulatedResponse(simResponse)
      setIsGeneratingResponse(true)
      
      // Esperar 1000ms para simular procesamiento
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Guardar la respuesta simulada permanentemente en el historial
      setSimulatedResponses(prev => ({
        ...prev,
        [currentQuestion.question_id]: simResponse
      }))
      
      // Limpiar el estado temporal y esperar un poco más antes de continuar
      setIsGeneratingResponse(false)
      setSimulatedResponse('')
      
      // Esperar un poco más antes de procesar la siguiente pregunta
      await new Promise(resolve => setTimeout(resolve, 800))

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
        const errorData = await response.json()
        // AD-3: Handle error with suggestion
        if (errorData.detail && typeof errorData.detail === 'object' && 'suggestion' in errorData.detail) {
          setApiError(errorData.detail.detail)
          setSuggestion(errorData.detail.suggestion)
        } else if (errorData.detail && typeof errorData.detail === 'object' && 'message' in errorData.detail) {
          setValidationError(errorData.detail.message)
          setSuggestion(null)
        } else {
          setApiError(errorData.detail || 'Error al enviar respuesta')
          setSuggestion(null)
        }
        return
      }

      // Clear errors and suggestion on success
      setApiError('')
      setSuggestion(null)

      const apiResult: AnswerResponse = await response.json()

      if (apiResult.completed) {
        // Generate filename
        await generateFilename(newAnswers)
      } else if (apiResult.next_question) {
        // Move to next question
        setCurrentQuestion(apiResult.next_question)
      }
    } catch (error) {
      setApiError('Error de conexión')
    } finally {
      setIsLoading(false)
      // No limpiar isGeneratingResponse ni simulatedResponse aquí ya que se manejan manualmente
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
      setFolderStructure(result.folder_structure || [])  // URSALL
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

      // Usar endpoint URSALL si hay folder_structure
      const endpoint = folderStructure.length > 0
        ? `${API_BASE_URL}/api/ursall/upload-final`
        : `${API_BASE_URL}/api/upload-final`

      const body = folderStructure.length > 0
        ? {
            file_id: fileId,
            filename: suggestedName,
            dropbox_path: suggestedPath,
            folder_structure: folderStructure
          }
        : {
            file_id: fileId,
            new_filename: suggestedName,
            dropbox_path: suggestedPath
          }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
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
        {questionHistory.map((q, index) => (
          <React.Fragment key={q.question_id}>
            <div className="question-animation-container">
              <MessageBubble 
                role="assistant" 
                content={q.question_text}
                helpText={q.help_text}
                examples={q.examples}
              />
              {answers[q.question_id] && (
                <MessageBubble role="user" content={answers[q.question_id]} />
              )}
              {simulatedResponses[q.question_id] && (
                <MessageBubble role="assistant" content={simulatedResponses[q.question_id]} />
              )}
            </div>
            {/* Separador visual entre respuesta y siguiente pregunta */}
            {index < questionHistory.length - 1 && (
              <div className="question-separator" style={{
                margin: '20px auto',
                width: '80%',
                height: '1px',
                background: 'rgba(255, 255, 255, 0.1)',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
              }}></div>
            )}
          </React.Fragment>
        ))}

        {/* Pregunta actual */}
        {currentQuestion && (
          <div className="current-question-container">
            <MessageBubble
              role="assistant"
              content={currentQuestion.question_text}
              helpText={currentQuestion.help_text}
              examples={currentQuestion.examples}
            />
          </div>
        )}

        {/* Errores de validación */}
        {validationError && (
          <MessageBubble
            role="assistant"
            content=""
            error={validationError}
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

        {/* Indicador de generando respuesta con respuesta simulada */}
        {isGeneratingResponse && (
          <>
            <MessageBubble
              role="assistant"
              content={
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span style={{ color: 'var(--text-tertiary)' }}>Generando respuesta...</span>
                </div>
              }
            />
            {simulatedResponse && (
              <MessageBubble
                role="assistant"
                content={simulatedResponse}
              />
            )}
          </>
        )}

        {/* Indicador de carga para otras operaciones */}
        {isLoading && !isGeneratingResponse && (
          <MessageBubble
            role="assistant"
            content={
              <div className="loading-container">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span style={{ 
                    color: 'var(--text-primary)', 
                    fontWeight: 500,
                    fontSize: '1.05rem'
                  }}>Cargando preguntas</span>
                </div>
                <div style={{ 
                  fontSize: '0.9rem', 
                  color: 'var(--text-tertiary)',
                  textAlign: 'center',
                  maxWidth: '280px'
                }} className="loading-text">
                  Preparando la siguiente pregunta para ti...
                </div>
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
          disabled={isLoading || isGeneratingResponse}
        />
      )}
    </>
  )
}
