/**
 * Test suite for AD-2: QuestionFlow component
 * TDD RED phase - These tests MUST fail initially
 *
 * Tests the sequential question asking flow:
 * - Renders one question at a time
 * - Validates input before submitting
 * - Advances through question sequence
 * - Shows suggested filename at the end
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QuestionFlow } from './QuestionFlow'

// Mock fetch
global.fetch = vi.fn()

describe('QuestionFlow Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Question Display', () => {
    it('Test #10: Frontend muestra QuestionFlow después de subir archivo', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()

      // Mock first question response
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      } as Response)

      // Act
      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/tipo de documento/i)).toBeInTheDocument()
      })
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/questions/start'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ file_id: fileId })
        })
      )
    })

    it('Test #11: Frontend muestra una pregunta a la vez con input', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      } as Response)

      // Act
      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/tipo de documento/i)).toBeInTheDocument()
      })

      // Should have input field
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute('required')

      // Should have submit button
      const submitButton = screen.getByRole('button', { name: /siguiente|enviar/i })
      expect(submitButton).toBeInTheDocument()
    })
  })

  describe('Input Validation', () => {
    it('Test #12: Frontend valida respuesta antes de enviar al backend', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      const input = screen.getByRole('textbox')
      const submitButton = screen.getByRole('button', { name: /siguiente|enviar/i })

      // Act - Try to submit with empty input
      await user.click(submitButton)

      // Assert - Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/mínimo 2 caracteres/i)).toBeInTheDocument()
      })

      // Should NOT call backend
      expect(fetch).toHaveBeenCalledTimes(1) // Only initial start call

      // Act - Try with 1 character
      await user.type(input, 'F')
      await user.click(submitButton)

      // Assert - Still shows error
      await waitFor(() => {
        expect(screen.getByText(/mínimo 2 caracteres/i)).toBeInTheDocument()
      })
      expect(fetch).toHaveBeenCalledTimes(1)
    })

    it('Test #12b: Frontend valida formato de fecha YYYY-MM-DD', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'date',
          question_text: '¿Cuál es la fecha del documento? (YYYY-MM-DD)',
          required: true,
          validation: { format: 'YYYY-MM-DD' }
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      const input = screen.getByRole('textbox')
      const submitButton = screen.getByRole('button', { name: /siguiente|enviar/i })

      // Act - Try invalid date formats
      await user.type(input, '15-01-2025')
      await user.click(submitButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/formato.*YYYY-MM-DD/i)).toBeInTheDocument()
      })

      // Should NOT call backend
      expect(fetch).toHaveBeenCalledTimes(1) // Only initial start
    })
  })

  describe('Question Flow Navigation', () => {
    it('Test #13: Frontend avanza a siguiente pregunta tras respuesta válida', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      // Mock first question
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      } as Response)

      // Mock answer response with next question
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          next_question: {
            question_id: 'client',
            question_text: '¿Cuál es el nombre del cliente?',
            required: true,
            validation: { min_length: 2 }
          },
          completed: false
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      // Wait for first question
      await waitFor(() => {
        expect(screen.getByText(/tipo de documento/i)).toBeInTheDocument()
      })

      // Act - Answer first question
      const input = screen.getByRole('textbox')
      await user.type(input, 'Factura')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should show second question
      await waitFor(() => {
        expect(screen.getByText(/nombre del cliente/i)).toBeInTheDocument()
      })

      // Should NOT show first question anymore
      expect(screen.queryByText(/tipo de documento/i)).not.toBeInTheDocument()
    })

    it('Test #14: Frontend muestra nombre sugerido al completar todas las preguntas', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      // Mock last question
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'date',
          question_text: '¿Cuál es la fecha del documento? (YYYY-MM-DD)',
          required: true,
          validation: { format: 'YYYY-MM-DD' }
        })
      } as Response)

      // Mock answer response - completed
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          next_question: null,
          completed: true
        })
      } as Response)

      // Mock generate name response
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          suggested_name: '2025-01-15_Factura_Acme_Corp.pdf',
          original_extension: '.pdf'
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByText(/fecha del documento/i)).toBeInTheDocument()
      })

      // Act - Answer last question
      const input = screen.getByRole('textbox')
      await user.type(input, '2025-01-15')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should show suggested name
      await waitFor(() => {
        expect(screen.getByText(/2025-01-15_Factura_Acme_Corp\.pdf/)).toBeInTheDocument()
      })

      // Should call onComplete callback
      expect(onComplete).toHaveBeenCalledWith('2025-01-15_Factura_Acme_Corp.pdf')
    })
  })

  describe('Error Handling', () => {
    it('should show error message when backend fails', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'File not found'
        })
      } as Response)

      // Act
      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument()
        expect(screen.getByText(/file not found/i)).toBeInTheDocument()
      })
    })

    it('should handle network errors gracefully', async () => {
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()

      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

      // Act
      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/error.*conexión/i)).toBeInTheDocument()
      })
    })
  })
})
