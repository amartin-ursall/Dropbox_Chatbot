/**
 * Tests for QuestionFlow editing functionality - AD-9
 * Tests US-10: Corregir antes de confirmar
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QuestionFlow } from './QuestionFlow'

describe('QuestionFlow - Edit Functionality (AD-9)', () => {
  const mockFileId = 'test-file-123'
  const mockOnComplete = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('Test 36: shows back button after answering first question', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          completed: false,
          next_question: {
            question_id: 'client',
            question_text: '¿Cuál es el cliente?',
            required: true,
            validation: { min_length: 2 }
          }
        })
      })

    global.fetch = mockFetch

    render(
      <QuestionFlow
        fileId={mockFileId}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    expect(screen.queryByText(/← atrás/i)).toBeNull()

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Factura' } })
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }))

    await waitFor(() => {
      expect(screen.getByText(/cliente/i)).toBeTruthy()
    })

    expect(screen.getByText(/← atrás/i)).toBeTruthy()
  })

  it('Test 37: can go back to previous question and preserves answer', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          completed: false,
          next_question: {
            question_id: 'client',
            question_text: '¿Cuál es el cliente?',
            required: true,
            validation: { min_length: 2 }
          }
        })
      })

    global.fetch = mockFetch

    render(
      <QuestionFlow
        fileId={mockFileId}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'Factura' } })
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }))

    await waitFor(() => {
      expect(screen.getByText(/cliente/i)).toBeTruthy()
    })

    const backButton = screen.getByText(/← atrás/i)
    fireEvent.click(backButton)

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    const inputAfterBack = screen.getByRole('textbox') as HTMLInputElement
    expect(inputAfterBack.value).toBe('Factura')
  })

  it('Test 38: shows edit button in preview', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          completed: true
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          suggested_name: '2025-01-15_Factura_ClienteA.pdf',
          suggested_path: '/Documentos/Facturas'
        })
      })

    global.fetch = mockFetch

    render(
      <QuestionFlow
        fileId={mockFileId}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Factura' } })
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }))

    await waitFor(() => {
      expect(screen.getByText(/vista previa/i)).toBeTruthy()
    })

    expect(screen.getByText(/✏️ editar/i)).toBeTruthy()
  })

  it('Test 39: edit button goes back to first question with preserved answer', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          completed: true
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          suggested_name: '2025-01-15_Factura_ClienteA.pdf',
          suggested_path: '/Documentos/Facturas'
        })
      })

    global.fetch = mockFetch

    render(
      <QuestionFlow
        fileId={mockFileId}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Factura' } })
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }))

    await waitFor(() => {
      expect(screen.getByText(/vista previa/i)).toBeTruthy()
    })

    const editButton = screen.getByText(/✏️ editar/i)
    fireEvent.click(editButton)

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    const inputAfterEdit = screen.getByRole('textbox') as HTMLInputElement
    expect(inputAfterEdit.value).toBe('Factura')
  })

  it('Test 40: back button works correctly', async () => {
    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          question_id: 'doc_type',
          question_text: '¿Qué tipo de documento es?',
          required: true,
          validation: { min_length: 2 }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          completed: false,
          next_question: {
            question_id: 'client',
            question_text: '¿Cuál es el cliente?',
            required: true,
            validation: { min_length: 2 }
          }
        })
      })

    global.fetch = mockFetch

    render(
      <QuestionFlow
        fileId={mockFileId}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    )

    await waitFor(() => {
      expect(screen.getByText(/tipo de documento/i)).toBeTruthy()
    })

    // Initially no back button on first question
    expect(screen.queryByText(/← atrás/i)).toBeNull()

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Factura' } })
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }))

    await waitFor(() => {
      expect(screen.getByText(/cliente/i)).toBeTruthy()
    })

    // Back button appears on second question
    const backButton = screen.getByText(/← atrás/i) as HTMLButtonElement
    expect(backButton).toBeTruthy()
    expect(backButton.disabled).toBe(false)
  })
})
