import { motion } from 'framer-motion'
import { classNames } from '@/utils'
import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  padding?: 'sm' | 'md' | 'lg' | 'none'
  hover?: boolean
  onClick?: () => void
}

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

export function Card({ children, className, padding = 'md', hover = false, onClick }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={classNames(
        'bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700',
        paddingStyles[padding],
        hover && 'hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 cursor-pointer',
        'transition-all duration-200',
        className
      )}
      onClick={onClick}
      whileHover={hover ? { scale: 1.01 } : undefined}
    >
      {children}
    </motion.div>
  )
}
