/**
 * E2E Test for AD-3: Validación Avanzada
 * TDD RED phase - These tests MUST fail initially
 *
 * Test #16: Usuario ingresa fecha futura y ve error
 * Test #17: Usuario acepta sugerencia y avanza
 */
import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test.describe('AD-3: Advanced Validation E2E', () => {
  test('Test #16: should reject future date and show error message', async ({ page }) => {
    /**
     * Scenario: Validación avanzada de fecha
     *   Given el usuario está respondiendo la pregunta de fecha
     *   When ingresa una fecha futura
     *   Then el sistema rechaza la respuesta
     *   And muestra un mensaje: "La fecha no puede estar en el futuro"
     */

    // Given: Usuario está en la aplicación
    await page.goto('http://localhost:5173')

    // Upload file
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    // Navigate through questions to reach date question
    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 5000 })
    await page.getByRole('textbox').fill('Factura')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()
    await page.getByRole('textbox').fill('Test Client')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/fecha del documento/i)).toBeVisible()

    // When: Usuario ingresa fecha futura
    const dateInput = page.getByRole('textbox')
    await dateInput.fill('2030-01-01')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe mostrar error
    await expect(page.getByText(/futuro/i)).toBeVisible({ timeout: 3000 })

    // And: No debe avanzar (sigue en la misma pregunta)
    await expect(page.getByText(/fecha del documento/i)).toBeVisible()
  })

  test('Test #17: should accept suggestion and proceed', async ({ page }) => {
    /**
     * Scenario: Sugerencias de corrección
     *   Given el usuario ingresa una respuesta inválida
     *   When el sistema detecta un error común
     *   Then muestra una sugerencia de corrección
     *   And el usuario puede aceptar la sugerencia
     */

    // Given: Usuario está en la aplicación
    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    // When: Usuario ingresa tipo de documento con números
    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 5000 })
    const docTypeInput = page.getByRole('textbox')
    await docTypeInput.fill('Factura123')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe mostrar error y sugerencia
    await expect(page.getByText(/solo letras/i)).toBeVisible({ timeout: 3000 })
    await expect(page.getByText(/sugerencia/i)).toBeVisible()
    await expect(page.getByText('Factura')).toBeVisible()

    // When: Usuario acepta la sugerencia
    const useSuggestionButton = page.getByRole('button', { name: /usar.*sugerencia/i })
    await useSuggestionButton.click()

    // Then: Input debe tener la sugerencia
    await expect(docTypeInput).toHaveValue('Factura')

    // And: Usuario puede enviar y avanzar
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Should move to next question
    await expect(page.getByText(/nombre del cliente/i)).toBeVisible({ timeout: 3000 })
  })

  test('should validate document type contains only letters', async ({ page }) => {
    /**
     * Scenario: Validación de tipo de documento
     *   Given el usuario está respondiendo tipo de documento
     *   When ingresa texto con números o caracteres especiales
     *   Then el sistema rechaza la respuesta
     */

    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 5000 })

    // Try with special characters
    const input = page.getByRole('textbox')
    await input.fill('Doc@2025')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/solo letras/i)).toBeVisible({ timeout: 2000 })

    // Should still be on same question
    await expect(page.getByText(/tipo de documento/i)).toBeVisible()
  })

  test('should validate client name character restrictions', async ({ page }) => {
    /**
     * Scenario: Validación de nombre de cliente
     *   Given el usuario está respondiendo nombre del cliente
     *   When ingresa texto con caracteres prohibidos
     *   Then el sistema rechaza la respuesta
     */

    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    // Navigate to client question
    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 5000 })
    await page.getByRole('textbox').fill('Factura')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()

    // Try with prohibited symbols
    const clientInput = page.getByRole('textbox')
    await clientInput.fill('Client@Email.com')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Should show error
    await expect(page.getByText(/letras.*números/i)).toBeVisible({ timeout: 2000 })

    // Should still be on client question
    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()
  })

  test('should allow valid client with hyphens and dots', async ({ page }) => {
    /**
     * Verify that valid characters (hyphens, dots) are accepted
     */

    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 5000 })
    await page.getByRole('textbox').fill('Factura')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()

    // Use valid client name with hyphens and dots
    await page.getByRole('textbox').fill('Acme-Corp.')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Should advance to date question
    await expect(page.getByText(/fecha del documento/i)).toBeVisible({ timeout: 3000 })
  })
})
