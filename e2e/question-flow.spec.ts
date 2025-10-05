/**
 * E2E Test for AD-2: Guía por preguntas
 * TDD RED phase - This test MUST fail initially
 *
 * Test #15: E2E - Flujo completo desde upload hasta nombre sugerido
 *
 * Scenario: Recolección de datos para renombrado
 *   Given el usuario ha subido un archivo temporal
 *   When el chatbot pregunta por tipo de documento, cliente y fecha
 *   And el usuario responde a todas las preguntas
 *   Then el sistema genera un nombre de archivo nuevo con esos datos
 *   And el chatbot muestra el nombre sugerido al usuario
 */
import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test.describe('AD-2: Question Flow E2E', () => {
  test('should complete full question flow and show suggested filename', async ({ page }) => {
    // Given: El usuario está en la aplicación
    await page.goto('http://localhost:5173')

    // When: Sube un archivo
    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testFilePath)

    // Then: Debe ver confirmación de upload
    await expect(page.getByText(/archivo subido/i)).toBeVisible({ timeout: 5000 })

    // And: Debe ver la primera pregunta sobre tipo de documento
    await expect(page.getByText(/tipo de documento/i)).toBeVisible({ timeout: 3000 })

    // When: Responde "Factura" a la primera pregunta
    const docTypeInput = page.getByRole('textbox')
    await docTypeInput.fill('Factura')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe ver la segunda pregunta sobre cliente
    await expect(page.getByText(/nombre del cliente/i)).toBeVisible({ timeout: 3000 })

    // When: Responde "Acme Corp" a la segunda pregunta
    const clientInput = page.getByRole('textbox')
    await clientInput.fill('Acme Corp')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe ver la tercera pregunta sobre fecha
    await expect(page.getByText(/fecha del documento/i)).toBeVisible({ timeout: 3000 })

    // When: Responde con fecha válida
    const dateInput = page.getByRole('textbox')
    await dateInput.fill('2025-01-15')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe ver el nombre sugerido
    await expect(page.getByText(/2025-01-15_Factura_Acme_Corp\.pdf/)).toBeVisible({ timeout: 3000 })

    // And: Debe tener formato correcto {fecha}_{tipo}_{cliente}.{ext}
    const suggestedName = await page.getByText(/2025-01-15_Factura_Acme_Corp\.pdf/).textContent()
    expect(suggestedName).toMatch(/\d{4}-\d{2}-\d{2}_\w+_[\w_]+\.pdf/)
  })

  test('should validate date format before proceeding', async ({ page }) => {
    // Given: Usuario está en la pregunta de fecha
    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    await expect(page.getByText(/tipo de documento/i)).toBeVisible()
    await page.getByRole('textbox').fill('Factura')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()
    await page.getByRole('textbox').fill('Test Client')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/fecha del documento/i)).toBeVisible()

    // When: Intenta enviar fecha con formato incorrecto
    const dateInput = page.getByRole('textbox')
    await dateInput.fill('15-01-2025') // Wrong format
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: Debe mostrar error de validación
    await expect(page.getByText(/formato.*YYYY-MM-DD/i)).toBeVisible({ timeout: 2000 })

    // And: No debe avanzar a la pantalla de nombre sugerido
    await expect(page.getByText(/2025-01-15_Factura/)).not.toBeVisible()
  })

  test('should sanitize special characters in suggested filename', async ({ page }) => {
    // Given: Usuario completa el flujo con caracteres especiales
    await page.goto('http://localhost:5173')

    const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf')
    await page.locator('input[type="file"]').setInputFiles(testFilePath)

    await expect(page.getByText(/tipo de documento/i)).toBeVisible()
    await page.getByRole('textbox').fill('Factura Electrónica')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/nombre del cliente/i)).toBeVisible()
    await page.getByRole('textbox').fill('Cliente & Asociados S.A.')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    await expect(page.getByText(/fecha del documento/i)).toBeVisible()
    await page.getByRole('textbox').fill('2025-01-15')
    await page.getByRole('button', { name: /siguiente|enviar/i }).click()

    // Then: El nombre debe estar sanitizado
    await expect(page.getByText(/2025-01-15_Factura_Electronica_Cliente_Asociados_SA\.pdf/)).toBeVisible({ timeout: 3000 })
  })
})
