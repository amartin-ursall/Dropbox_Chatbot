/**
 * Application constants
 * Centralized configuration
 */

// Use specific IP for network access
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.VITE_BACKEND_URL || 'http://192.168.0.98:8000')

export const ALLOWED_FILE_EXTENSIONS = [
  '.pdf',
  '.docx',
  '.xlsx',
  '.jpg',
  '.jpeg',
  '.png',
  '.txt'
]

export const ALLOWED_FILE_ACCEPT = ALLOWED_FILE_EXTENSIONS.join(',')
