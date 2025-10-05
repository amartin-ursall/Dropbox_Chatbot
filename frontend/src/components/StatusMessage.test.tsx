/**
 * Tests for StatusMessage component - AD-7
 * Tests US-09: Mensajes de estado en el chat
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { StatusMessage } from './StatusMessage'

describe('StatusMessage Component', () => {
  it('Test 24: displays success message with correct styling', () => {
    render(
      <StatusMessage
        type="success"
        message="Archivo subido exitosamente"
      />
    )

    expect(screen.getByText(/archivo subido exitosamente/i)).toBeTruthy()
    expect(screen.getByText('✅')).toBeTruthy()
  })

  it('Test 25: displays error message with correct styling', () => {
    render(
      <StatusMessage
        type="error"
        message="Error al subir archivo"
      />
    )

    expect(screen.getByText(/error al subir archivo/i)).toBeTruthy()
    expect(screen.getByText('❌')).toBeTruthy()
  })

  it('Test 26: displays warning message with correct styling', () => {
    render(
      <StatusMessage
        type="warning"
        message="Advertencia: Revisa los datos"
      />
    )

    expect(screen.getByText(/advertencia: revisa los datos/i)).toBeTruthy()
    expect(screen.getByText('⚠️')).toBeTruthy()
  })

  it('Test 27: displays info message with correct styling', () => {
    render(
      <StatusMessage
        type="info"
        message="Procesando archivo..."
      />
    )

    expect(screen.getByText(/procesando archivo/i)).toBeTruthy()
    expect(screen.getByText('ℹ️')).toBeTruthy()
  })

  it('Test 28: shows close button when onClose is provided', () => {
    const mockOnClose = vi.fn()
    render(
      <StatusMessage
        type="success"
        message="Test message"
        onClose={mockOnClose}
      />
    )

    const closeButton = screen.getByLabelText(/cerrar mensaje/i)
    expect(closeButton).toBeTruthy()
  })

  it('Test 29: calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn()
    render(
      <StatusMessage
        type="success"
        message="Test message"
        onClose={mockOnClose}
      />
    )

    const closeButton = screen.getByLabelText(/cerrar mensaje/i)
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('Test 30: does not show close button when onClose is not provided', () => {
    render(
      <StatusMessage
        type="success"
        message="Test message"
      />
    )

    const closeButton = screen.queryByLabelText(/cerrar mensaje/i)
    expect(closeButton).toBeNull()
  })

  it('Test 31: has correct CSS class for message type', () => {
    const { container } = render(
      <StatusMessage
        type="error"
        message="Test error"
      />
    )

    expect(container.querySelector('.status-message')).toBeTruthy()
    expect(container.querySelector('.status-error')).toBeTruthy()
  })

  it('Test 32: renders message text correctly', () => {
    const testMessage = "Este es un mensaje de prueba con caracteres especiales: áéíóú ñ @#$"
    render(
      <StatusMessage
        type="info"
        message={testMessage}
      />
    )

    expect(screen.getByText(testMessage)).toBeTruthy()
  })
})
