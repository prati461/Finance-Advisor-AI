import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Card } from '@/components/common/Card'
import { formatCurrency } from '@/utils'
import { EXPENSE_CATEGORY_COLORS } from '@/constants'
import { useTheme } from '@/contexts/ThemeContext'

interface DataPoint {
  name: string
  value: number
}

interface ExpensePieChartProps {
  data: DataPoint[]
  loading?: boolean
}

export function ExpensePieChart({ data, loading }: ExpensePieChartProps) {
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

  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <Card>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Expense Distribution
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={EXPENSE_CATEGORY_COLORS[entry.name] || '#6b7280'}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: isDark ? '#f3f4f6' : '#111827',
              }}
              formatter={(value: number) => [
                `${formatCurrency(value)} (${((value / total) * 100).toFixed(1)}%)`,
              ]}
            />
            <Legend
              formatter={(value: string) => (
                <span className="text-sm text-gray-600 dark:text-gray-400">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
