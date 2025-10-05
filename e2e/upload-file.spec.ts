/**
 * E2E Tests for file upload flow (AD-1)
 * Red phase - These tests should FAIL initially
 */
import { test, expect } from '@playwright/test'
import path from 'path'

test.describe('AD-1: Subir archivo desde el chat', () => {
  test('Test 11: Flujo completo - seleccionar → enviar → ver confirmación', async ({ page }) => {
    /**
     * Gherkin: Complete scenario
     * Given el usuario inicia el flujo del chatbot
     * When el usuario selecciona un archivo y lo envía
     * Then el sistema guarda el archivo en almacenamiento temporal
     * And el chatbot confirma la recepción del archivo
     */
    // Given: usuario inicia el flujo
    await page.goto('http://localhost:5173')

    // Verify chatbot interface is visible
    await expect(page.getByRole('heading', { name: /chatbot|dropbox organizer/i })).toBeVisible()

    // When: usuario selecciona un archivo
    const testFilePath = path.join(__dirname, 'fixtures', 'test-invoice.pdf')
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testFilePath)

    // Verify preview is shown
    await expect(page.getByText(/test-invoice\.pdf/i)).toBeVisible()
    await expect(page.getByText(/\d+\s*(bytes|KB|MB)/i)).toBeVisible()

    // When: usuario envía el archivo
    const uploadButton = page.getByRole('button', { name: /enviar|upload/i })
    await uploadButton.click()

    // Then & And: confirmación de recepción
    await expect(page.getByText(/archivo recibido|upload successful/i)).toBeVisible({ timeout: 5000 })
    await expect(page.getByText(/test-invoice\.pdf/i)).toBeVisible()

    // Verify chat message from bot
    await expect(page.locator('.chat-message.bot').last()).toContainText(/recibí tu archivo|file received/i)
  })

  test('Test 12: Error visible si archivo demasiado grande', async ({ page }) => {
    /**
     * Error scenario: validación de tamaño
     * Given el usuario inicia el flujo
     * When el usuario intenta subir un archivo > 50MB
     * Then el sistema muestra un error claro
     */
    // Given
    await page.goto('http://localhost:5173')

    // When: intenta subir archivo grande (mocked con interceptor)
    await page.route('**/api/upload-temp', async (route) => {
      await route.fulfill({
        status: 413,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'File size exceeds 50MB limit'
        })
      })
    })

    const testFilePath = path.join(__dirname, 'fixtures', 'large-file.pdf')
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testFilePath)

    const uploadButton = page.getByRole('button', { name: /enviar|upload/i })
    await uploadButton.click()

    // Then: error visible
    const errorAlert = page.getByRole('alert')
    await expect(errorAlert).toBeVisible()
    await expect(errorAlert).toContainText(/50MB|tamaño|size limit/i)
  })

  test('Test 12b: Error visible si extensión no permitida', async ({ page }) => {
    /**
     * Error scenario: validación de extensión
     */
    // Given
    await page.goto('http://localhost:5173')

    // When: intenta subir archivo .exe
    await page.route('**/api/upload-temp', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'File extension not allowed. Please use: .pdf, .docx, .xlsx, .jpg, .png'
        })
      })
    })

    const testFilePath = path.join(__dirname, 'fixtures', 'malware.exe')
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testFilePath)

    const uploadButton = page.getByRole('button', { name: /enviar|upload/i })
    await uploadButton.click()

    // Then: error visible
    const errorAlert = page.getByRole('alert')
    await expect(errorAlert).toBeVisible()
    await expect(errorAlert).toContainText(/extension|extensión|not allowed/i)
  })
})
