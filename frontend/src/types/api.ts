/**
 * API types and interfaces
 * Refactored from component for reusability
 * AD-2: Added question flow types
 * AD-3: Added suggestion support
 */

export interface FileMetadata {
  file_id: string
  original_name: string
  size: number
  file_size?: number  // Alias para size
  extension: string
  mime_type?: string
}

export interface ApiError {
  error?: string
  detail?: string | { detail: string; suggestion?: string }
}

// AD-2: Question flow types
export interface Question {
  question_id: string
  question_text: string
  required: boolean
  validation: {
    min_length?: number
    format?: string
    only_letters?: boolean  // AD-3
  }
}

export interface AnswerResponse {
  next_question: Question | null
  completed: boolean
}

export interface SuggestedNameResponse {
  suggested_name: string
  original_extension: string
  suggested_path?: string  // AD-4
  full_path?: string       // AD-4
}
