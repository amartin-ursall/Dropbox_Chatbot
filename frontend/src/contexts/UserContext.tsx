/**
 * UserContext
 * Context to share user information across components
 */
import React, { createContext, useContext, useState, useEffect } from 'react'

interface UserInfo {
  name: string
  email: string
  profile_photo_url?: string
}

interface UserContextType {
  userInfo: UserInfo | null
  setUserInfo: (info: UserInfo | null) => void
  isLoading: boolean
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Fetch user info on mount
    fetchUserInfo()
  }, [])

  const fetchUserInfo = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/api/user/info')
      if (response.ok) {
        const data = await response.json()
        setUserInfo(data)
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <UserContext.Provider value={{ userInfo, setUserInfo, isLoading }}>
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
