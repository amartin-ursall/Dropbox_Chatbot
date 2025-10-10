/**
 * UserContext
 * Context to share user information across components
 * Handles automatic loading with cache
 */
import React, { createContext, useContext, useState, useEffect } from 'react'

interface UserInfo {
  name: string
  email: string
  used_space: number
  allocated_space: number
  account_type: string
  profile_photo_url?: string
}

interface CachedUserInfo {
  data: UserInfo
  timestamp: number
}

interface UserContextType {
  userInfo: UserInfo | null
  setUserInfo: (info: UserInfo | null) => void
  isLoading: boolean
  authError: boolean
  refreshUserInfo: () => Promise<void>
}

const UserContext = createContext<UserContextType | undefined>(undefined)

// Use environment variable or specific IP for network access
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://192.168.0.98:8000'
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutos en milisegundos
const CACHE_KEY = 'dropbox_user_info_cache'

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true) // Start with loading true
  const [authError, setAuthError] = useState(false)

  useEffect(() => {
    // Load from cache first, then fetch fresh data
    loadFromCacheAndFetch()
  }, [])

  const loadFromCacheAndFetch = async () => {
    // Try to load from cache first
    const cachedData = localStorage.getItem(CACHE_KEY)
    if (cachedData) {
      try {
        const cached: CachedUserInfo = JSON.parse(cachedData)
        const now = Date.now()

        // If cache is valid, use it immediately
        if (now - cached.timestamp < CACHE_DURATION) {
          console.log('Loading user info from cache')
          setUserInfo(cached.data)
          setIsLoading(false)
          return // Don't fetch if cache is fresh
        }
      } catch (error) {
        console.error('Error loading cache:', error)
      }
    }

    // Fetch fresh data
    await fetchUserInfo()
  }

  const fetchUserInfo = async () => {
    try {
      setIsLoading(true)
      setAuthError(false)

      console.log('Fetching fresh user info from API')
      const response = await fetch(`${API_BASE_URL}/api/user/info`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache'
        }
      })

      if (response.status === 200) {
        const data = await response.json()
        console.log('Fresh user data received:', data)
        setUserInfo(data)

        // Save to cache
        const cacheData: CachedUserInfo = {
          data,
          timestamp: Date.now()
        }
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
        setAuthError(false)
      } else if (response.status === 401) {
        console.log('User not authenticated')
        setAuthError(true)
        setUserInfo(null)
      } else {
        console.error(`Error fetching user info: ${response.status} - ${response.statusText}`)
        setAuthError(true)
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      setAuthError(true)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshUserInfo = async () => {
    await fetchUserInfo()
  }

  return (
    <UserContext.Provider value={{ 
      userInfo, 
      setUserInfo, 
      isLoading, 
      authError, 
      refreshUserInfo 
    }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
