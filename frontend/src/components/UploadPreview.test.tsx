/**
 * Tests for UploadPreview component - AD-4
 * Tests preview display and confirmation buttons
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { UploadPreview } from './UploadPreview'

describe('UploadPreview Component', () => {
  const mockProps = {
    suggestedName: '2025-01-15_Factura_Acme-Corp.pdf',
    suggestedPath: '/Documentos/Facturas',
    onConfirm: vi.fn(),
    onCancel: vi.fn()
  }

  it('Test 11: displays suggested filename', () => {
    render(<UploadPreview {...mockProps} />)
    expect(screen.getByText(/2025-01-15_Factura_Acme-Corp\.pdf/)).toBeTruthy()
  })

  it('Test 12: displays suggested Dropbox path', () => {
    render(<UploadPreview {...mockProps} />)
    expect(screen.getByText(/\/Documentos\/Facturas/)).toBeTruthy()
  })

  it('Test 13: shows Confirmar button', () => {
    render(<UploadPreview {...mockProps} />)
    const confirmButton = screen.getByRole('button', { name: /confirmar/i })
    expect(confirmButton).toBeTruthy()
  })

  it('Test 14: shows Cancelar button', () => {
    render(<UploadPreview {...mockProps} />)
    const cancelButton = screen.getByRole('button', { name: /cancelar/i })
    expect(cancelButton).toBeTruthy()
  })

  it('Test 15: calls onConfirm when Confirmar is clicked', () => {
    render(<UploadPreview {...mockProps} />)
    const confirmButton = screen.getByRole('button', { name: /confirmar/i })
    fireEvent.click(confirmButton)
    expect(mockProps.onConfirm).toHaveBeenCalledTimes(1)
  })

  it('Test 16: calls onCancel when Cancelar is clicked', () => {
    render(<UploadPreview {...mockProps} />)
    const cancelButton = screen.getByRole('button', { name: /cancelar/i })
    fireEvent.click(cancelButton)
    expect(mockProps.onCancel).toHaveBeenCalledTimes(1)
  })

  it('displays file icon emoji', () => {
    render(<UploadPreview {...mockProps} />)
    expect(screen.getByText(/📄/)).toBeTruthy()
  })

  it('displays folder icon emoji', () => {
    render(<UploadPreview {...mockProps} />)
    expect(screen.getByText(/📁/)).toBeTruthy()
  })

  it('renders with correct structure', () => {
    const { container } = render(<UploadPreview {...mockProps} />)
    expect(container.querySelector('.upload-preview')).toBeTruthy()
  })

  it('shows proper labels for name and path', () => {
    render(<UploadPreview {...mockProps} />)
    expect(screen.getByText(/nombre sugerido/i)).toBeTruthy()
    expect(screen.getByText(/ruta en dropbox/i)).toBeTruthy()
  })

  it('Test 21: disables buttons when uploading', () => {
    render(<UploadPreview {...mockProps} isUploading={true} />)
    const confirmButton = screen.getByRole('button', { name: /subiendo/i })
    const cancelButton = screen.getByRole('button', { name: /cancelar/i })

    expect((confirmButton as HTMLButtonElement).disabled).toBe(true)
    expect((cancelButton as HTMLButtonElement).disabled).toBe(true)
  })

  it('Test 22: shows "Subiendo..." text when uploading', () => {
    render(<UploadPreview {...mockProps} isUploading={true} />)
    expect(screen.getByText(/subiendo\.\.\./i)).toBeTruthy()
  })

  it('Test 23: shows "Confirmar" text when not uploading', () => {
    render(<UploadPreview {...mockProps} isUploading={false} />)
    expect(screen.getByText(/^confirmar$/i)).toBeTruthy()
  })

  it('Test 41: shows edit button when onEdit is provided', () => {
    const mockOnEdit = vi.fn()
    render(<UploadPreview {...mockProps} onEdit={mockOnEdit} />)

    const editButton = screen.getByText(/✏️ editar/i)
    expect(editButton).toBeTruthy()
  })

  it('Test 42: calls onEdit when edit button is clicked', () => {
    const mockOnEdit = vi.fn()
    render(<UploadPreview {...mockProps} onEdit={mockOnEdit} />)

    const editButton = screen.getByText(/✏️ editar/i)
    fireEvent.click(editButton)

    expect(mockOnEdit).toHaveBeenCalledTimes(1)
  })

  it('Test 43: does not show edit button when onEdit is not provided', () => {
    render(<UploadPreview {...mockProps} />)

    expect(screen.queryByText(/✏️ editar/i)).toBeNull()
  })

  it('Test 44: edit button is disabled when uploading', () => {
    const mockOnEdit = vi.fn()
    render(<UploadPreview {...mockProps} onEdit={mockOnEdit} isUploading={true} />)

    const editButton = screen.getByText(/✏️ editar/i) as HTMLButtonElement
    expect(editButton.disabled).toBe(true)
  })
})
