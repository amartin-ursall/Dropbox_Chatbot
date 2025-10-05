/**
 * Application constants
 * Centralized configuration
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
