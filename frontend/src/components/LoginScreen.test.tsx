/**
 * Tests for LoginScreen component - AD-5
 * Tests Dropbox OAuth2 login UI
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { LoginScreen } from './LoginScreen'

describe('LoginScreen Component', () => {
  const mockOnLoginSuccess = vi.fn()

  it('Test 10: displays Dropbox logo or icon', () => {
    render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    // Look for Dropbox branding (use getAllByText since "Dropbox" appears multiple times)
    expect(screen.getAllByText(/dropbox/i).length).toBeGreaterThan(0)
  })

  it('Test 11: shows "Conectar con Dropbox" button', () => {
    render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    const connectButton = screen.getByRole('button', { name: /conectar.*dropbox/i })
    expect(connectButton).toBeTruthy()
  })

  it('Test 12: shows informative message', () => {
    render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    expect(screen.getByText(/Conecta tu cuenta/i)).toBeTruthy()
  })

  it('Test 13: button triggers login flow', () => {
    // Mock window.location
    delete (window as any).location
    window.location = { href: '' } as any

    render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    const connectButton = screen.getByRole('button', { name: /conectar.*dropbox/i })

    fireEvent.click(connectButton)

    // Should redirect to backend OAuth endpoint
    expect(window.location.href).toContain('/auth/dropbox/login')
  })

  it('renders with login-screen class', () => {
    const { container } = render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    expect(container.querySelector('.login-screen')).toBeTruthy()
  })

  it('button is not disabled by default', () => {
    render(<LoginScreen onLoginSuccess={mockOnLoginSuccess} />)
    const connectButton = screen.getByRole('button', { name: /conectar.*dropbox/i })
    expect((connectButton as HTMLButtonElement).disabled).toBe(false)
  })
})
