/**
 * Test suite for AD-3: Advanced Validation in QuestionFlow
 * TDD RED phase - These tests MUST fail initially
 *
 * Tests advanced validation features:
 * - Future date rejection
 * - Improved error messages
 * - Suggestion display and acceptance
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QuestionFlow } from './QuestionFlow'

// Mock fetch
global.fetch = vi.fn()

describe('QuestionFlow Advanced Validation (AD-3)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Client-Side Advanced Validation', () => {
    it('Test #12: Frontend valida fecha futura antes de enviar', async () => {
      /**
       * Given: Usuario está en la pregunta de fecha
       * When: Ingresa una fecha futura
       * Then: Muestra error sin llamar al backend
       */
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

      // Act - Enter future date
      const input = screen.getByRole('textbox')
      const futureDate = '2030-01-01'
      await user.type(input, futureDate)
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/futuro/i)).toBeInTheDocument()
      })

      // Should NOT call backend (only initial start call)
      expect(fetch).toHaveBeenCalledTimes(1)
    })

    it('Test #12b: Frontend valida tipo de documento solo letras', async () => {
      /**
       * Given: Usuario está en pregunta de tipo doc
       * When: Ingresa tipo con números
       * Then: Muestra error antes de enviar al backend
       */
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
          validation: { min_length: 2, only_letters: true }
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      // Act
      const input = screen.getByRole('textbox')
      await user.type(input, 'Factura123')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/solo letras/i)).toBeInTheDocument()
      })

      expect(fetch).toHaveBeenCalledTimes(1) // Only start call
    })
  })

  describe('Improved Error Messages', () => {
    it('Test #13: Frontend muestra mensaje de error mejorado', async () => {
      /**
       * Given: Usuario ingresa respuesta inválida
       * When: Se detecta el error
       * Then: Muestra mensaje descriptivo con ejemplo
       */
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
          validation: { min_length: 2, only_letters: true }
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      // Act
      const input = screen.getByRole('textbox')
      await user.type(input, 'Doc@123')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should show detailed message
      await waitFor(() => {
        const errorMessage = screen.getByText(/solo letras/i)
        expect(errorMessage).toBeInTheDocument()
        // Should include example
        expect(screen.getByText(/ejemplo/i) || screen.getByText(/factura/i)).toBeInTheDocument()
      })
    })
  })

  describe('Suggestion Display and Acceptance', () => {
    it('Test #14: Frontend muestra sugerencia cuando disponible', async () => {
      /**
       * Given: Backend retorna error con sugerencia
       * When: Se muestra al usuario
       * Then: Aparece la sugerencia claramente visible
       */
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      // Mock start
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2, only_letters: true }
        })
      } as Response)

      // Mock answer with suggestion
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'El tipo debe contener solo letras y espacios',
          suggestion: 'Factura'
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      // Act - Submit invalid input
      const input = screen.getByRole('textbox')
      await user.type(input, 'Factura123')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should show suggestion
      await waitFor(() => {
        expect(screen.getByText(/sugerencia/i)).toBeInTheDocument()
        expect(screen.getByText('Factura')).toBeInTheDocument()
      })
    })

    it('Test #15: Frontend permite usar sugerencia con un click', async () => {
      /**
       * Given: Hay una sugerencia visible
       * When: Usuario hace click en "Usar sugerencia"
       * Then: El input se llena con la sugerencia
       */
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
          validation: { min_length: 2, only_letters: true }
        })
      } as Response)

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'El tipo debe contener solo letras',
          suggestion: 'Factura'
        })
      } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      const input = screen.getByRole('textbox')
      await user.type(input, 'Factura123')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Wait for suggestion to appear
      await waitFor(() => {
        expect(screen.getByText(/sugerencia/i)).toBeInTheDocument()
      })

      // Act - Click "Use suggestion" button
      const useSuggestionButton = screen.getByRole('button', { name: /usar.*sugerencia/i })
      await user.click(useSuggestionButton)

      // Assert - Input should be filled with suggestion
      expect(input).toHaveValue('Factura')

      // Suggestion should disappear
      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /usar.*sugerencia/i })).not.toBeInTheDocument()
      })
    })

    it('Test #15b: Frontend envía sugerencia aceptada al backend', async () => {
      /**
       * Given: Usuario acepta sugerencia
       * When: Hace click en siguiente
       * Then: Envía la sugerencia al backend correctamente
       */
      // Arrange
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      vi.mocked(fetch)
        // Start
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            question_id: 'doc_type',
            question_text: '¿Qué tipo de documento es?',
            required: true,
            validation: { min_length: 2, only_letters: true }
          })
        } as Response)
        // First answer with error + suggestion
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({
            detail: 'El tipo debe contener solo letras',
            suggestion: 'Factura'
          })
        } as Response)
        // Second answer (after using suggestion)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            next_question: {
              question_id: 'client',
              question_text: 'Cliente?',
              required: true,
              validation: { min_length: 2 }
            },
            completed: false
          })
        } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument()
      })

      const input = screen.getByRole('textbox')
      await user.type(input, 'Factura123')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /usar.*sugerencia/i })).toBeInTheDocument()
      })

      // Use suggestion
      await user.click(screen.getByRole('button', { name: /usar.*sugerencia/i }))

      // Submit
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      // Assert - Should call backend with suggestion
      await waitFor(() => {
        const calls = vi.mocked(fetch).mock.calls
        const answerCall = calls.find(call =>
          call[0]?.toString().includes('/api/questions/answer')
        )
        expect(answerCall).toBeDefined()
        const body = JSON.parse(answerCall![1]!.body as string)
        expect(body.answer).toBe('Factura')
      })
    })
  })

  describe('Error Messages from Backend', () => {
    it('should display backend validation error with suggestion', async () => {
      /**
       * Test that backend errors with suggestions are properly displayed
       */
      const fileId = '123e4567-e89b-12d3-a456-426614174000'
      const onComplete = vi.fn()
      const user = userEvent.setup()

      vi.mocked(fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            question_id: 'date',
            question_text: 'Fecha?',
            required: true,
            validation: { format: 'YYYY-MM-DD' }
          })
        } as Response)
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({
            detail: 'Formato inválido',
            suggestion: '2025-01-15'
          })
        } as Response)

      render(<QuestionFlow fileId={fileId} onComplete={onComplete} />)

      await waitFor(() => expect(screen.getByRole('textbox')).toBeInTheDocument())

      await user.type(screen.getByRole('textbox'), '15-01-2025')
      await user.click(screen.getByRole('button', { name: /siguiente|enviar/i }))

      await waitFor(() => {
        expect(screen.getByText(/formato inválido/i)).toBeInTheDocument()
        expect(screen.getByText('2025-01-15')).toBeInTheDocument()
      })
    })
  })
})
