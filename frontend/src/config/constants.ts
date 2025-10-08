/**
 * Application constants
 * Centralized configuration
 */

// Use domain-based URL for network access, fallback to localhost for local development
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.VITE_BACKEND_URL || 'http://dropboxaiorganizer.com:8000')

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
