import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, PiggyBank, Calendar } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { StatCard } from '@/components/common/StatCard'
import { Card } from '@/components/common/Card'
import { Select } from '@/components/common/Select'
import { IncomeVsExpenseChart } from '@/components/charts/IncomeVsExpenseChart'
import { ExpensePieChart } from '@/components/charts/ExpensePieChart'
import { MonthlyTrendChart } from '@/components/charts/MonthlyTrendChart'
import { useMonthlySummary } from '@/hooks/useSummary'
import { useIncomes } from '@/hooks/useIncomes'
import { useExpenses } from '@/hooks/useExpenses'
import { useBudgets } from '@/hooks/useBudgets'
import { formatCurrency, getMonthName, getCurrentMonth, getCurrentYear } from '@/utils'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

const months = Array.from({ length: 12 }, (_, i) => ({
  value: i + 1,
  label: getMonthName(i + 1),
}))

const currentYear = getCurrentYear()
const years = Array.from({ length: 5 }, (_, i) => ({
  value: currentYear - 2 + i,
  label: String(currentYear - 2 + i),
}))

export function MonthlySummaryPage() {
  const [month, setMonth] = useState(getCurrentMonth())
  const [year, setYear] = useState(currentYear)

  const { data: summary, isLoading, error, refetch } = useMonthlySummary({ month, year })
  const { data: incomesData } = useIncomes({ page: 1, page_size: 100 })
  const { data: expensesData } = useExpenses({ page: 1, page_size: 100 })
  const { data: budgetsData } = useBudgets({ month, year })

  const expensePieData = useMemo(() => {
    if (!expensesData?.items) return []
    const categoryTotals: Record<string, number> = {}
    expensesData.items.forEach((expense) => {
      categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount
    })
    return Object.entries(categoryTotals).map(([name, value]) => ({ name, value }))
  }, [expensesData])

  const chartData = useMemo(() => {
    const monthsArr = []
    for (let i = 5; i >= 0; i--) {
      const d = new Date()
      d.setMonth(d.getMonth() - i)
      monthsArr.push({
        month: getMonthName(d.getMonth() + 1).substring(0, 3),
        income: Math.random() * 50000 + 30000,
        expense: Math.random() * 30000 + 10000,
        savings: Math.random() * 20000 + 5000,
      } as any)
    }
    return monthsArr
  }, [])

  const savingsPercentage = summary
    ? summary.income_total > 0
      ? ((summary.income_total - summary.expense_total) / summary.income_total) * 100
      : 0
    : 0

  const totalBudget = budgetsData?.items?.reduce((sum, b) => sum + b.budget_amount, 0) || 0
  const totalSpent = expensesData?.items?.reduce((sum, e) => sum + e.amount, 0) || 0
  const budgetRemaining = totalBudget - totalSpent

  return (
    <div className="space-y-6">
      <PageHeader
        title="Monthly Summary"
        subtitle={`Financial overview for ${getMonthName(month)} ${year}`}
      />

      {/* Month/Year Selector */}
      <Card padding="sm">
        <div className="flex flex-col sm:flex-row gap-4 p-2">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-gray-400" />
            <Select
              options={months}
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="w-40"
            />
            <Select
              options={years}
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-28"
            />
          </div>
        </div>
      </Card>

      {error ? (
        <ErrorMessage onRetry={refetch} />
      ) : isLoading ? (
        <LoadingSpinner fullPage />
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Income"
              value={formatCurrency(summary?.income_total || 0)}
              icon={TrendingUp}
              trend="up"
              trendValue={`${savingsPercentage.toFixed(1)}% savings rate`}
              colorClass="green"
              index={0}
            />
            <StatCard
              title="Total Expense"
              value={formatCurrency(summary?.expense_total || 0)}
              icon={TrendingDown}
              trend="down"
              trendValue={`${summary ? ((summary.expense_total / (summary.income_total || 1)) * 100).toFixed(1) : 0}% of income`}
              colorClass="red"
              index={1}
            />
            <StatCard
              title="Total Savings"
              value={formatCurrency(summary?.savings_total || 0)}
              icon={PiggyBank}
              trend={savingsPercentage >= 0 ? 'up' : 'down'}
              trendValue={savingsPercentage >= 0 ? `${savingsPercentage.toFixed(1)}%` : 'Negative'}
              colorClass="blue"
              index={2}
            />
            <StatCard
              title="Budget Remaining"
              value={formatCurrency(Math.max(budgetRemaining, 0))}
              icon={Calendar}
              colorClass="purple"
              index={3}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <IncomeVsExpenseChart data={chartData} loading={isLoading} />
            <ExpensePieChart data={expensePieData} loading={isLoading} />
          </div>

          <MonthlyTrendChart data={chartData} loading={isLoading} />
        </>
      )}
    </div>
  )
}
