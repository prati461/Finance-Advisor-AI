import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, type LucideIcon } from 'lucide-react'
import { Card } from './Card'
import { classNames } from '@/utils'

interface StatCardProps {
  title: string
  value: string
  icon: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  colorClass?: string
  index?: number
}

const colorMap = {
  blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  green: 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  red: 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  yellow: 'bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400',
  indigo: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  colorClass = 'blue',
  index = 0,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
    >
      <Card padding="md" className="relative overflow-hidden group">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
            {trend && trendValue && (
              <div className="flex items-center gap-1">
                {trend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : trend === 'down' ? (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                ) : null}
                <span
                  className={classNames(
                    'text-xs font-medium',
                    trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-500'
                  )}
                >
                  {trendValue}
                </span>
              </div>
            )}
          </div>
          <div
            className={classNames(
              'p-3 rounded-xl transition-transform group-hover:scale-110 duration-200',
              colorMap[colorClass as keyof typeof colorMap] || colorMap.blue
            )}
          >
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </Card>
    </motion.div>
  )
}
