import { Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  fullPage?: boolean
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

export function LoadingSpinner({ size = 'md', className = '', fullPage = false }: LoadingSpinnerProps) {
  if (fullPage) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Loader2 className={`${sizeMap[size]} animate-spin text-primary-600 dark:text-primary-400`} />
        </motion.div>
      </div>
    )
  }

  return (
    <Loader2
      className={`${sizeMap[size]} animate-spin text-primary-600 dark:text-primary-400 ${className}`}
    />
  )
}
