import { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Target,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  Lightbulb,
  AlertTriangle,
  Sparkles,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { StatCard } from '@/components/common/StatCard'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { PageHeader } from '@/components/common/PageHeader'
import { IncomeVsExpenseChart } from '@/components/charts/IncomeVsExpenseChart'
import { ExpensePieChart } from '@/components/charts/ExpensePieChart'
import { MonthlyTrendChart } from '@/components/charts/MonthlyTrendChart'
import { BudgetProgressChart } from '@/components/charts/BudgetProgressChart'
import { useMonthlySummary, useHistoricalSummary } from '@/hooks/useSummary'
import { useIncomes } from '@/hooks/useIncomes'
import { useExpenses } from '@/hooks/useExpenses'
import { useBudgets } from '@/hooks/useBudgets'
import { useAuth } from '@/contexts/AuthContext'
import { useFinancialHealth, useRecommendations } from '@/hooks/useAI'
import { formatCurrency, formatDate, getCurrentMonth, getCurrentYear, getMonthShortName } from '@/utils'
import { EmptyState } from '@/components/common/EmptyState'
import { ErrorMessage } from '@/components/common/ErrorMessage'

const currentMonth = getCurrentMonth()
const currentYear = getCurrentYear()

export function DashboardPage() {
  const { user } = useAuth()
  const { data: summary, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useMonthlySummary({
    month: currentMonth,
    year: currentYear,
  })
  const { data: historicalData, isLoading: historicalLoading, error: historicalError } = useHistoricalSummary(6)
  const { data: incomesData, isLoading: incomesLoading } = useIncomes({ page: 1, page_size: 5 })
  const { data: expensesData, isLoading: expensesLoading } = useExpenses({ page: 1, page_size: 5 })
  const { data: budgetsData, isLoading: budgetsLoading } = useBudgets({
    month: currentMonth,
    year: currentYear,
  })
  const { data: healthData, isLoading: healthLoading } = useFinancialHealth()
  const { data: recommendationsData, isLoading: recsLoading } = useRecommendations()

  // Use real historical data if available, fallback to summary data
  const chartData = useMemo(() => {
    if (historicalData && historicalData.length > 0) {
      return historicalData
    }
    // Fallback if no historical data
    return []
  }, [historicalData])

  const expensePieData = useMemo(() => {
    if (!expensesData?.items) return []
    const categoryTotals: Record<string, number> = {}
    expensesData.items.forEach((expense) => {
      categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount
    })
    return Object.entries(categoryTotals).map(([name, value]) => ({ name, value }))
  }, [expensesData])

  const budgetChartData = useMemo(() => {
    if (!budgetsData?.items || !expensesData?.items) return []
    const expenseByCategory: Record<string, number> = {}
    expensesData.items.forEach((e) => {
      expenseByCategory[e.category] = (expenseByCategory[e.category] || 0) + e.amount
    })
    return budgetsData.items.map((b) => ({
      category: b.category,
      budget: b.budget_amount,
      spent: expenseByCategory[b.category] || 0,
      percentage: b.budget_amount > 0 ? ((expenseByCategory[b.category] || 0) / b.budget_amount) * 100 : 0,
    }))
  }, [budgetsData, expensesData])

  const savingsPercentage = summary
    ? summary.income_total > 0
      ? ((summary.income_total - summary.expense_total) / summary.income_total) * 100
      : 0
    : 0

  const recentTransactions = useMemo(() => {
    const transactions = [
      ...(incomesData?.items?.map((i) => ({
        id: `income-${i.id}`,
        type: 'income' as const,
        description: i.source,
        category: i.category,
        amount: i.amount,
        date: i.received_date,
      })) || []),
      ...(expensesData?.items?.map((e) => ({
        id: `expense-${e.id}`,
        type: 'expense' as const,
        description: e.merchant || e.description || e.category,
        category: e.category,
        amount: e.amount,
        date: e.spent_at,
      })) || []),
    ]
    return transactions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 5)
  }, [incomesData, expensesData])

  const healthScore = healthData?.overall_score ?? null
  const topSuggestions = recommendationsData?.priority_goals?.slice(0, 3) ?? []
  const spendingTips = recommendationsData?.spending_tips?.slice(0, 3) ?? []

  if (summaryError) {
    return <ErrorMessage title="Failed to load dashboard" onRetry={refetchSummary} />
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Welcome back, {user?.full_name?.split(' ')[0] || 'User'}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Here's your financial overview for {getMonthShortName(currentMonth)} {currentYear}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/incomes?add=true">
            <Button variant="primary" size="sm" leftIcon={<Plus className="h-4 w-4" />}>
              Add Income
            </Button>
          </Link>
          <Link to="/expenses?add=true">
            <Button variant="secondary" size="sm" leftIcon={<Plus className="h-4 w-4" />}>
              Add Expense
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Income"
          value={summaryLoading ? '---' : formatCurrency(summary?.income_total || 0)}
          icon={TrendingUp}
          trend="up"
          trendValue={summaryLoading ? '...' : `${savingsPercentage.toFixed(1)}% savings rate`}
          colorClass="green"
          index={0}
        />
        <StatCard
          title="Total Expense"
          value={summaryLoading ? '---' : formatCurrency(summary?.expense_total || 0)}
          icon={TrendingDown}
          trend="down"
          trendValue={summaryLoading ? '...' : `${summary ? ((summary.expense_total / (summary.income_total || 1)) * 100).toFixed(1) : 0}% of income`}
          colorClass="red"
          index={1}
        />
        <StatCard
          title="Total Savings"
          value={summaryLoading ? '---' : formatCurrency(summary?.savings_total || 0)}
          icon={PiggyBank}
          trend={savingsPercentage >= 0 ? 'up' : 'down'}
          trendValue={summaryLoading ? '...' : `${Math.abs(savingsPercentage).toFixed(1)}%`}
          colorClass="blue"
          index={2}
        />
        <StatCard
          title="Budget Remaining"
          value={summaryLoading ? '---' : formatCurrency(
            (budgetsData?.items?.reduce((sum, b) => sum + b.budget_amount, 0) || 0) -
            (expensesData?.items?.reduce((sum, e) => sum + e.amount, 0) || 0)
          )}
          icon={Target}
          colorClass="purple"
          index={3}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncomeVsExpenseChart data={chartData} loading={summaryLoading} />
        <ExpensePieChart data={expensePieData} loading={expensesLoading} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MonthlyTrendChart data={chartData} loading={summaryLoading} />
        <BudgetProgressChart data={budgetChartData} loading={budgetsLoading} />
      </div>

      {/* AI Recommendations Card */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-5 w-5 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            AI Recommendations
          </h3>
          {!recsLoading && !healthLoading && healthScore !== null && (
            <span className="ml-auto flex items-center gap-2 text-sm">
              <span className="text-gray-500 dark:text-gray-400">Health Score:</span>
              <span className={`font-semibold ${
                healthScore >= 80 ? 'text-green-600' : healthScore >= 60 ? 'text-yellow-600' : 'text-red-600'
              }`}>{healthScore}/100</span>
            </span>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Priority Goals */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1.5">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              Priority Goals
            </h4>
            {recsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : topSuggestions.length > 0 ? (
              <div className="space-y-2">
                {topSuggestions.map((goal, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border-l-4 border-primary-500"
                  >
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{goal.goal}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{goal.action}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No recommendations yet. Add more data to get personalized insights.</p>
            )}
          </div>

          {/* Spending Tips */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Spending Tips
            </h4>
            {recsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 dark:bg-gray-700 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : spendingTips.length > 0 ? (
              <div className="space-y-2">
                {spendingTips.map((tip, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border-l-4 border-orange-500"
                  >
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{tip.category}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{tip.tip}</p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                      Potential savings: {formatCurrency(tip.potential_savings)}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No tips available. Start tracking expenses to get suggestions.</p>
            )}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-700">
          <Link
            to="/financial-health"
            className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400 font-medium"
          >
            View full financial health analysis →
          </Link>
        </div>
      </Card>

      {/* Recent Transactions & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Transactions */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Recent Transactions
            </h3>
            <Link
              to="/incomes"
              className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400 font-medium"
            >
              View All
            </Link>
          </div>
          {recentTransactions.length === 0 ? (
            <EmptyState
              title="No transactions yet"
              description="Add your first income or expense to get started"
            />
          ) : (
            <div className="space-y-3">
              {recentTransactions.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        tx.type === 'income'
                          ? 'bg-green-100 dark:bg-green-900/30'
                          : 'bg-red-100 dark:bg-red-900/30'
                      }`}
                    >
                      {tx.type === 'income' ? (
                        <ArrowUpRight className="h-4 w-4 text-green-600 dark:text-green-400" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-red-600 dark:text-red-400" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {tx.description}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {tx.category} · {formatDate(tx.date)}
                      </p>
                    </div>
                    </div>
                  <span
                    className={`text-sm font-semibold ${
                      tx.type === 'income'
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-red-600 dark:text-red-400'
                    }`}
                  >
                    {tx.type === 'income' ? '+' : '-'}{formatCurrency(tx.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Quick Actions */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link to="/incomes?add=true" className="block">
              <Button variant="outline" className="w-full" leftIcon={<TrendingUp className="h-4 w-4" />}>
                Add Income
              </Button>
            </Link>
            <Link to="/expenses?add=true" className="block">
              <Button variant="outline" className="w-full" leftIcon={<TrendingDown className="h-4 w-4" />}>
                Add Expense
              </Button>
            </Link>
            <Link to="/budgets?add=true" className="block">
              <Button variant="outline" className="w-full" leftIcon={<Target className="h-4 w-4" />}>
                Set Budget
              </Button>
            </Link>
            <Link to="/monthly-summary" className="block">
              <Button variant="outline" className="w-full" leftIcon={<PiggyBank className="h-4 w-4" />}>
                View Summary
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}
