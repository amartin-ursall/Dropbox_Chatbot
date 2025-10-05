/**
 * E2E tests for upload preview flow - AD-4
 */
import { test, expect } from '@playwright/test'

test.describe('Upload Preview Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173')
  })

  test('Test 17: Complete flow shows preview with name and path', async ({ page }) => {
    // Upload file
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test-factura.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('fake pdf content')
    })

    // Wait for file upload
    await page.waitForSelector('text=tipo de documento', { timeout: 5000 })

    // Answer questions
    await page.fill('input[type="text"]', 'Factura')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('text=cliente', { timeout: 3000 })
    await page.fill('input[type="text"]', 'Acme Corp')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('text=fecha', { timeout: 3000 })
    await page.fill('input[type="text"]', '2025-01-15')
    await page.click('button:has-text("Siguiente")')

    // Verify preview appears
    await expect(page.locator('text=/2025-01-15_Factura_Acme-Corp/')).toBeVisible()
    await expect(page.locator('text=/\\/Documentos\\/Facturas/')).toBeVisible()
  })

  test('Test 18: Preview shows Confirmar and Cancelar buttons', async ({ page }) => {
    // Upload and answer questions (same as above)
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test')
    })

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Contrato')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Test Client')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', '2025-01-20')
    await page.click('button:has-text("Siguiente")')

    // Verify buttons
    await expect(page.locator('button:has-text("Confirmar")')).toBeVisible()
    await expect(page.locator('button:has-text("Cancelar")')).toBeVisible()
  })

  test('Test 19: Click Confirmar triggers confirmation', async ({ page }) => {
    // Upload and complete flow
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test')
    })

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Recibo')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Client')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', '2025-01-25')
    await page.click('button:has-text("Siguiente")')

    // Click Confirmar
    await page.click('button:has-text("Confirmar")')

    // Verify confirmation message appears
    // (AD-5 will implement actual upload, here we just verify the click works)
    await expect(page.locator('text=/preparando|confirmado/i')).toBeVisible({ timeout: 3000 })
  })

  test('Test 20: Click Cancelar resets flow', async ({ page }) => {
    // Upload and complete flow
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test')
    })

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Factura')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Client')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', '2025-01-10')
    await page.click('button:has-text("Siguiente")')

    // Click Cancelar
    await page.click('button:has-text("Cancelar")')

    // Verify flow resets - should see upload input again
    await expect(page.locator('input[type="file"]')).toBeVisible({ timeout: 3000 })
  })

  test('Different document types show correct paths', async ({ page }) => {
    // Test Nómina → /Documentos/Nóminas
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test')
    })

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Nómina')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Empleado')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', '2025-01-31')
    await page.click('button:has-text("Siguiente")')

    // Verify path for Nómina
    await expect(page.locator('text=/\\/Documentos\\/Nóminas/')).toBeVisible()
  })

  test('Unknown document types show Otros path', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('test')
    })

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Documento Raro')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', 'Client')
    await page.click('button:has-text("Siguiente")')

    await page.waitForSelector('input[type="text"]')
    await page.fill('input[type="text"]', '2025-02-01')
    await page.click('button:has-text("Siguiente")')

    // Verify Otros path
    await expect(page.locator('text=/\\/Documentos\\/Otros/')).toBeVisible()
  })
})
