import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { formatCurrency } from '@/utils'
import { EXPENSE_CATEGORY_COLORS } from '@/constants'
import { useTheme } from '@/contexts/ThemeContext'

interface BudgetData {
  category: string
  budget: number
  spent: number
  percentage: number
}

interface BudgetProgressChartProps {
  data: BudgetData[]
  loading?: boolean
}

export function BudgetProgressChart({ data, loading }: BudgetProgressChartProps) {
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
        Budget Distribution
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
            <XAxis
              type="number"
              tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />
            <YAxis
              dataKey="category"
              type="category"
              tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={80}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: isDark ? '#f3f4f6' : '#111827',
              }}
              formatter={(_: number, name: string) => [
                name === 'percentage' ? `${data[0]?.percentage?.toFixed(1)}%` : '',
              ]}
            />
            <Bar dataKey="percentage" name="Usage" radius={[0, 4, 4, 0]} maxBarSize={20}>
              {data.map((entry) => (
                <Cell
                  key={entry.category}
                  fill={
                    entry.percentage > 90
                      ? '#ef4444'
                      : entry.percentage > 75
                      ? '#f59e0b'
                      : EXPENSE_CATEGORY_COLORS[entry.category] || '#10b981'
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
