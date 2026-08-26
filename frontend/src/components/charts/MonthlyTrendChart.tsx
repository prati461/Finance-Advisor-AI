import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { formatCurrency } from '@/utils'
import { useTheme } from '@/contexts/ThemeContext'

interface DataPoint {
  month: string
  income: number
  expense: number
  savings: number
}

interface MonthlyTrendChartProps {
  data: DataPoint[]
  loading?: boolean
}

export function MonthlyTrendChart({ data, loading }: MonthlyTrendChartProps) {
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  if (loading) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-5 w-40 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-72 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Savings Trend
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <defs>
              <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
            <XAxis
              dataKey="month"
              tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: isDark ? '#f3f4f6' : '#111827',
              }}
              formatter={(value: number) => [formatCurrency(value)]}
            />
            <Area
              type="monotone"
              dataKey="savings"
              stroke="#10b981"
              fill="url(#savingsGradient)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
