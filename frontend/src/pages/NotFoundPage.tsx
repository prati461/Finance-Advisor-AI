import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/common/Button'

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
      <div className="text-center max-w-md">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', duration: 0.8 }}
          className="mb-8"
        >
          <div className="text-8xl font-bold text-primary-200 dark:text-primary-900 select-none">
            404
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Page Not Found
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex items-center justify-center gap-3"
        >
          <Link to="/">
            <Button leftIcon={<Home className="h-4 w-4" />}>
              Go Home
            </Button>
          </Link>
          <Button
            variant="secondary"
            onClick={() => window.history.back()}
            leftIcon={<ArrowLeft className="h-4 w-4" />}
          >
            Go Back
          </Button>
        </motion.div>
      </div>
    </div>
  )
}
