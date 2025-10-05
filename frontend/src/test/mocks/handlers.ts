/**
 * Default MSW handlers
 */
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('http://localhost:8000/api/upload-temp', async ({ request }) => {
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return HttpResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    return HttpResponse.json({
      file_id: '550e8400-e29b-41d4-a716-446655440000',
      original_name: file.name,
      size: file.size,
      extension: '.' + file.name.split('.').pop()
    })
  })
]
