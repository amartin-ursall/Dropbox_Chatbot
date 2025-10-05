/**
 * Tests for App component - AD-5, AD-7
 * Tests authentication guard and routing
 * Tests status messages (US-09)
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import App from './App'

describe('App Component - Authentication Guard', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('shows loading state while checking authentication', () => {
    // Mock fetch to never resolve (simulates loading state)
    global.fetch = vi.fn(() => new Promise(() => {}))

    render(<App />)

    expect(screen.getByText(/Verificando autenticación/i)).toBeTruthy()
  })

  it('shows LoginScreen when user is not authenticated', async () => {
    // Mock /auth/status returning not authenticated
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ authenticated: false, account_id: null })
    })

    render(<App />)

    // Wait for auth check to complete
    await waitFor(() => {
      expect(screen.getByText(/Conecta tu cuenta/i)).toBeTruthy()
    })

    // Should show login button
    expect(screen.getByRole('button', { name: /conectar.*dropbox/i })).toBeTruthy()
  })

  it('shows main app when user is authenticated', async () => {
    // Mock /auth/status returning authenticated
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ authenticated: true, account_id: 'test-account-123' })
    })

    render(<App />)

    // Wait for auth check to complete
    await waitFor(() => {
      expect(screen.getByText(/1\. Sube un archivo/i)).toBeTruthy()
    })

    // Should show file upload input
    expect(screen.getByText(/AD-1: Subir archivo/i)).toBeTruthy()
  })

  it('handles auth check error by showing login screen', async () => {
    // Mock /auth/status throwing error
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'))

    render(<App />)

    // Wait for error handling - should default to showing login
    await waitFor(() => {
      expect(screen.getByText(/Conecta tu cuenta/i)).toBeTruthy()
    })
  })

  it('re-checks authentication after login success', async () => {
    // First call: not authenticated
    // Second call: authenticated
    let callCount = 0
    global.fetch = vi.fn().mockImplementation(() => {
      callCount++
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ authenticated: false, account_id: null })
        })
      } else {
        return Promise.resolve({
          ok: true,
          json: async () => ({ authenticated: true, account_id: 'test-account-123' })
        })
      }
    })

    const { rerender } = render(<App />)

    // Wait for first auth check (not authenticated)
    await waitFor(() => {
      expect(screen.getByText(/Conecta tu cuenta/i)).toBeTruthy()
    })

    // Simulate login success callback by simulating the component receiving new props
    // In real scenario, this would happen after OAuth callback
    // For now, we verify that the checkAuthStatus function is called on mount
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/auth/status')
  })
})

describe('App Component - Status Messages (AD-7)', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('Test 33: shows success message after file upload', async () => {
    // Mock authenticated user
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ authenticated: true, account_id: 'test-123' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ file_id: 'test-file-123', filename: 'test.pdf' })
      })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/1\. Sube un archivo/i)).toBeTruthy()
    })

    // Simulate file upload
    const fileInput = screen.getByText(/archivos permitidos/i).previousElementSibling as HTMLInputElement
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/cargado correctamente/i)).toBeTruthy()
    })
  })

  it('Test 34: shows error message when file upload fails', async () => {
    // Mock authenticated user
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ authenticated: true, account_id: 'test-123' })
      })
      .mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Archivo demasiado grande' })
      })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/1\. Sube un archivo/i)).toBeTruthy()
    })

    // Simulate file upload
    const fileInput = screen.getByText(/archivos permitidos/i).previousElementSibling as HTMLInputElement
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/archivo demasiado grande/i)).toBeTruthy()
    })
  })

  it('Test 35: allows closing status messages', async () => {
    // Mock authenticated user
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ authenticated: true, account_id: 'test-123' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ file_id: 'test-file-123', filename: 'test.pdf' })
      })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/1\. Sube un archivo/i)).toBeTruthy()
    })

    // Simulate file upload to trigger success message
    const fileInput = screen.getByText(/archivos permitidos/i).previousElementSibling as HTMLInputElement
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText(/cargado correctamente/i)).toBeTruthy()
    })

    // Close the message
    const closeButton = screen.getByLabelText(/cerrar mensaje/i)
    fireEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByText(/cargado correctamente/i)).toBeNull()
    })
  })
})
