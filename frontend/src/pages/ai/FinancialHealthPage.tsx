import { motion } from 'framer-motion'
import { Heart, TrendingUp, TrendingDown, PiggyBank, Target, Lightbulb, AlertTriangle } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useFinancialHealth, useRecommendations } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import { useMonthlySummary } from '@/hooks/useSummary'
import { getCurrentMonth, getCurrentYear } from '@/utils'

const currentMonth = getCurrentMonth()
const currentYear = getCurrentYear()

function ScoreMeter({ score, color, label }: { score: number; color: string; label: string }) {
  const circumference = 2 * Math.PI * 54
  const progress = (score / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="none" stroke="currentColor" strokeWidth="8" className="text-gray-200 dark:text-gray-700" />
          <motion.circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <motion.span
              className="text-3xl font-bold"
              style={{ color }}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
              {score}
            </motion.span>
            <span className="block text-xs text-gray-500 dark:text-gray-400">/100</span>
          </div>
        </div>
      </div>
      <span className="mt-2 text-sm font-medium" style={{ color }}>{label}</span>
    </div>
  )
}

function ComponentBar({ label, score, note, color }: { label: string; score: number; note: string; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
        <span className="text-sm font-semibold" style={{ color }}>{score}/100</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <motion.div
          className="h-2 rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, delay: 0.3 }}
        />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400">{note}</p>
    </div>
  )
}

export function FinancialHealthPage() {
  const { data: health, isLoading, error, refetch } = useFinancialHealth()
  const { data: recommendations } = useRecommendations()
  const { data: summary, isLoading: summaryLoading } = useMonthlySummary({
    month: currentMonth,
    year: currentYear,
  })

  if (error) {
    return <ErrorMessage title="Failed to load financial health" onRetry={refetch} />
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial Health"
        subtitle="Comprehensive analysis of your financial well-being"
      />

      {isLoading ? (
        <LoadingSpinner />
      ) : health ? (
        <>
          {/* Score Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-1 flex flex-col items-center justify-center py-8">
              <ScoreMeter score={health.overall_score} color={health.color} label={health.category} />
              <p className="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center px-4">
                {health.summary}
              </p>
            </Card>

            <Card className="lg:col-span-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Score Breakdown</h3>
              <div className="space-y-4">
                <ComponentBar
                  label="Income Stability"
                  score={health.components.income_stability.score}
                  note={health.components.income_stability.note}
                  color="#10b981"
                />
                <ComponentBar
                  label="Expense Ratio"
                  score={health.components.expense_ratio.score}
                  note={health.components.expense_ratio.note}
                  color="#3b82f6"
                />
                <ComponentBar
                  label="Savings Ratio"
                  score={health.components.savings_ratio.score}
                  note={health.components.savings_ratio.note}
                  color="#8b5cf6"
                />
                <ComponentBar
                  label="Budget Utilization"
                  score={health.components.budget_utilization.score}
                  note={health.components.budget_utilization.note}
                  color="#f59e0b"
                />
                <ComponentBar
                  label="Investment Readiness"
                  score={health.components.investment_readiness.score}
                  note={health.components.investment_readiness.note}
                  color="#ec4899"
                />
              </div>
            </Card>
          </div>

          {/* Suggestions */}
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Personalized Suggestions
              </h3>
            </div>
            <div className="space-y-3">
              {health.suggestions.map((suggestion, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50"
                >
                  <AlertTriangle className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700 dark:text-gray-300">{suggestion}</p>
                </motion.div>
              ))}
            </div>
          </Card>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Income</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {summaryLoading ? '---' : formatCurrency(summary?.income_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                  <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Expenses</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {summaryLoading ? '---' : formatCurrency(summary?.expense_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <PiggyBank className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Savings</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {summaryLoading ? '---' : formatCurrency(summary?.savings_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  )
}

