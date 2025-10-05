/**
 * Frontend validation utilities
 * AD-2: Client-side validation before API calls
 * AD-3: Advanced validation (future dates, character restrictions)
 */
import type { Question } from '../types/api'

export interface ValidationResult {
  isValid: boolean
  error?: string
}

/**
 * Validate answer based on question requirements
 * AD-3: Enhanced with advanced validations
 */
export function validateAnswer(value: string, question: Question): ValidationResult {
  const trimmed = value.trim()

  // Check min_length
  if (question.validation.min_length) {
    if (trimmed.length < question.validation.min_length) {
      return {
        isValid: false,
        error: `La respuesta debe tener mínimo ${question.validation.min_length} caracteres`
      }
    }
  }

  // AD-3: Validate document type (only letters)
  if (question.question_id === 'doc_type' && question.validation.only_letters) {
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(trimmed)) {
      return {
        isValid: false,
        error: 'El tipo debe contener solo letras y espacios (sin números ni símbolos). Ejemplo: Factura'
      }
    }
    if (trimmed.length > 50) {
      return {
        isValid: false,
        error: 'El tipo debe tener máximo 50 caracteres'
      }
    }
  }

  // AD-3: Validate client (letters, numbers, spaces, hyphens, dots)
  if (question.question_id === 'client') {
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s.\-]+$/.test(trimmed)) {
      return {
        isValid: false,
        error: 'El cliente solo puede contener letras, números, espacios, guiones y puntos. Ejemplo: Acme Corp.'
      }
    }
    if (trimmed.length > 100) {
      return {
        isValid: false,
        error: 'El cliente debe tener máximo 100 caracteres'
      }
    }
  }

  // Check date format
  if (question.validation.format === 'YYYY-MM-DD') {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/
    if (!datePattern.test(value)) {
      return {
        isValid: false,
        error: 'Formato de fecha inválido. Usa YYYY-MM-DD (ejemplo: 2025-01-15)'
      }
    }

    // Validate it's a real date
    const [year, month, day] = value.split('-').map(Number)
    const date = new Date(year, month - 1, day)
    if (
      date.getFullYear() !== year ||
      date.getMonth() !== month - 1 ||
      date.getDate() !== day
    ) {
      return {
        isValid: false,
        error: 'Fecha inválida. Verifica el día y mes'
      }
    }

    // AD-3: Check date is not in the future
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    date.setHours(0, 0, 0, 0)

    if (date > today) {
      return {
        isValid: false,
        error: 'La fecha no puede estar en el futuro. Usa una fecha de hoy o anterior.'
      }
    }
  }

  return { isValid: true }
}
