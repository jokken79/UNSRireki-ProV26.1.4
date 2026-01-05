'use client'

import { useState } from 'react'
import { User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AvatarDisplayProps {
  photoUrl?: string | null
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-12 h-12 text-sm',
  lg: 'w-20 h-20 text-lg',
  xl: 'w-32 h-32 text-2xl',
}

const iconSizes = {
  sm: 16,
  md: 20,
  lg: 32,
  xl: 48,
}

export function AvatarDisplay({
  photoUrl,
  name,
  size = 'md',
  className,
}: AvatarDisplayProps) {
  const [imageError, setImageError] = useState(false)

  // Construct full URL for photo
  const getPhotoSrc = () => {
    if (!photoUrl) return null

    // If it's already a full URL or data URL, use as-is
    if (photoUrl.startsWith('http') || photoUrl.startsWith('data:')) {
      return photoUrl
    }

    // If it starts with /uploads, prepend the API URL
    if (photoUrl.startsWith('/uploads')) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      return `${apiUrl}${photoUrl}`
    }

    // Otherwise, assume it's a relative path to photos
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return `${apiUrl}/uploads/photos/${photoUrl}`
  }

  const photoSrc = getPhotoSrc()
  const showImage = photoSrc && !imageError

  // Get initials from name
  const getInitials = () => {
    if (!name) return ''
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return parts[0].substring(0, 2).toUpperCase()
  }

  return (
    <div
      className={cn(
        'relative rounded-full overflow-hidden flex items-center justify-center',
        'bg-slate-100 dark:bg-slate-700',
        'border-2 border-white dark:border-slate-600 shadow-sm',
        sizeClasses[size],
        className
      )}
    >
      {showImage ? (
        <img
          src={photoSrc}
          alt={name || 'Photo'}
          className="w-full h-full object-cover"
          onError={() => setImageError(true)}
        />
      ) : name ? (
        <span className="font-semibold text-slate-600 dark:text-slate-300">
          {getInitials()}
        </span>
      ) : (
        <User
          size={iconSizes[size]}
          className="text-slate-400 dark:text-slate-500"
        />
      )}
    </div>
  )
}

// Larger photo display for detail pages
export function PhotoDisplay({
  photoUrl,
  name,
  className,
}: {
  photoUrl?: string | null
  name?: string
  className?: string
}) {
  const [imageError, setImageError] = useState(false)

  const getPhotoSrc = () => {
    if (!photoUrl) return null
    if (photoUrl.startsWith('http') || photoUrl.startsWith('data:')) {
      return photoUrl
    }
    if (photoUrl.startsWith('/uploads')) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      return `${apiUrl}${photoUrl}`
    }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return `${apiUrl}/uploads/photos/${photoUrl}`
  }

  const photoSrc = getPhotoSrc()

  if (!photoSrc || imageError) {
    return (
      <div
        className={cn(
          'w-40 h-48 rounded-lg bg-slate-100 dark:bg-slate-700',
          'flex items-center justify-center',
          'border-2 border-dashed border-slate-300 dark:border-slate-600',
          className
        )}
      >
        <div className="text-center">
          <User size={48} className="mx-auto text-slate-400 mb-2" />
          <span className="text-xs text-slate-500">No Photo</span>
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'w-40 h-48 rounded-lg overflow-hidden shadow-md',
        'border-2 border-white dark:border-slate-600',
        className
      )}
    >
      <img
        src={photoSrc}
        alt={name || 'Photo'}
        className="w-full h-full object-cover"
        onError={() => setImageError(true)}
      />
    </div>
  )
}
