/**
 * Tests for FileUploadWidget component (AD-1)
 * Red phase - These tests should FAIL initially
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FileUploadWidget } from './FileUploadWidget'
import { rest } from 'msw'
import { setupServer } from 'msw/node'

// Mock API server
const server = setupServer(
  rest.post('http://localhost:8000/api/upload-temp', async (req, res, ctx) => {
    const formData = await req.formData()
    const file = formData.get('file') as File

    return res(
      ctx.json({
        file_id: '550e8400-e29b-41d4-a716-446655440000',
        original_name: file.name,
        size: file.size,
        extension: '.' + file.name.split('.').pop()
      })
    )
  })
)

beforeEach(() => {
  server.listen()
})

describe('FileUploadWidget', () => {
  it('Test 6: renderiza input de archivo', () => {
    /**
     * Gherkin: Given el usuario inicia el flujo del chatbot
     */
    // Act
    render(<FileUploadWidget onUploadComplete={vi.fn()} />)

    // Assert
    const fileInput = screen.getByLabelText(/subir archivo/i)
    expect(fileInput).toBeInTheDocument()
    expect(fileInput).toHaveAttribute('type', 'file')
    expect(fileInput).toHaveAttribute('accept') // Should have allowed extensions
  })

  it('Test 7: muestra preview con nombre y tamaño al seleccionar archivo', async () => {
    /**
     * Gherkin: When el usuario selecciona un archivo y lo envía (parte 1: selección)
     */
    // Arrange
    const user = userEvent.setup()
    render(<FileUploadWidget onUploadComplete={vi.fn()} />)

    const file = new File(['test content'], 'invoice.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByLabelText(/subir archivo/i)

    // Act
    await user.upload(fileInput, file)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/invoice\.pdf/i)).toBeInTheDocument()
      expect(screen.getByText(/12.*bytes|B/i)).toBeInTheDocument() // File size display
    })
  })

  it('Test 8: llama endpoint /upload-temp al enviar', async () => {
    /**
     * Gherkin: When el usuario selecciona un archivo y lo envía (parte 2: envío)
     */
    // Arrange
    const user = userEvent.setup()
    const mockOnComplete = vi.fn()
    render(<FileUploadWidget onUploadComplete={mockOnComplete} />)

    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByLabelText(/subir archivo/i)

    // Act
    await user.upload(fileInput, file)
    const uploadButton = screen.getByRole('button', { name: /enviar|upload/i })
    await user.click(uploadButton)

    // Assert
    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith(
        expect.objectContaining({
          file_id: '550e8400-e29b-41d4-a716-446655440000',
          original_name: 'test.pdf'
        })
      )
    })
  })

  it('Test 9: muestra mensaje de confirmación al recibir 200', async () => {
    /**
     * Gherkin: And el chatbot confirma la recepción del archivo
     */
    // Arrange
    const user = userEvent.setup()
    render(<FileUploadWidget onUploadComplete={vi.fn()} />)

    const file = new File(['data'], 'document.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    const fileInput = screen.getByLabelText(/subir archivo/i)

    // Act
    await user.upload(fileInput, file)
    const uploadButton = screen.getByRole('button', { name: /enviar|upload/i })
    await user.click(uploadButton)

    // Assert
    await waitFor(() => {
      expect(screen.getByText(/archivo recibido|upload successful/i)).toBeInTheDocument()
      expect(screen.getByText(/document\.docx/i)).toBeInTheDocument()
    })
  })

  it('Test 10: muestra error si falla upload (network error)', async () => {
    /**
     * Error handling: red, validación
     */
    // Arrange
    server.use(
      rest.post('http://localhost:8000/api/upload-temp', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Internal server error' }))
      })
    )

    const user = userEvent.setup()
    render(<FileUploadWidget onUploadComplete={vi.fn()} />)

    const file = new File(['data'], 'test.pdf', { type: 'application/pdf' })
    const fileInput = screen.getByLabelText(/subir archivo/i)

    // Act
    await user.upload(fileInput, file)
    const uploadButton = screen.getByRole('button', { name: /enviar|upload/i })
    await user.click(uploadButton)

    // Assert
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/error|falló/i)
    })
  })

  it('Test 10b: muestra error si archivo es demasiado grande', async () => {
    /**
     * Error handling: validación de tamaño
     */
    // Arrange
    server.use(
      rest.post('http://localhost:8000/api/upload-temp', (req, res, ctx) => {
        return res(ctx.status(413), ctx.json({ error: 'File size exceeds 50MB limit' }))
      })
    )

    const user = userEvent.setup()
    render(<FileUploadWidget onUploadComplete={vi.fn()} />)

    // Simulate large file (metadata only)
    const largeFile = new File(['x'.repeat(1000)], 'huge.pdf', { type: 'application/pdf' })
    Object.defineProperty(largeFile, 'size', { value: 51 * 1024 * 1024 })

    const fileInput = screen.getByLabelText(/subir archivo/i)

    // Act
    await user.upload(fileInput, largeFile)
    const uploadButton = screen.getByRole('button', { name: /enviar|upload/i })
    await user.click(uploadButton)

    // Assert
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/50MB|tamaño|size/i)
    })
  })
})
