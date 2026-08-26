import { motion } from 'framer-motion'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface ErrorMessageProps {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorMessage({
  title = 'Something went wrong',
  message = 'An error occurred while loading data.',
  onRetry,
}: ErrorMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center py-16 px-4"
    >
      <div className="text-red-400 dark:text-red-500 mb-4">
        <AlertTriangle className="h-16 w-16" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
        {title}
      </h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 text-center max-w-md">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors duration-200 text-sm font-medium"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </motion.div>
  )
}
