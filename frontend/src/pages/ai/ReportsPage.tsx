import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Calendar, FileSpreadsheet, BarChart3 } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Select } from '@/components/common/Select'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { useMonthlySummary } from '@/hooks/useSummary'
// Placeholder data - will be connected to real API in future
import { formatCurrency, getMonthName, getCurrentMonth, getCurrentYear } from '@/utils'
import { IncomeVsExpenseChart } from '@/components/charts/IncomeVsExpenseChart'
import { ExpensePieChart } from '@/components/charts/ExpensePieChart'

const currentYear = getCurrentYear()
const currentMonth = getCurrentMonth()

const MONTHS = Array.from({ length: 12 }, (_, i) => ({ value: String(i + 1), label: getMonthName(i + 1) }))
const YEARS = Array.from({ length: 5 }, (_, i) => ({ value: String(currentYear - i), label: String(currentYear - i) }))

export function ReportsPage() {
  const [month, setMonth] = useState(String(currentMonth))
  const [year, setYear] = useState(String(currentYear))
  const [format, setFormat] = useState('pdf')

  const { data: summary, isLoading } = useMonthlySummary({
    month: parseInt(month),
    year: parseInt(year),
  })

  // Placeholder chart data
  const chartData = [
    { month: getMonthName(parseInt(month)).substring(0, 3), income: summary?.income_total || 0, expense: summary?.expense_total || 0, savings: summary?.savings_total || 0 },
  ]

  const handleExport = () => {
    // Placeholder for export functionality
    alert(`Report generation for ${getMonthName(parseInt(month))} ${year} in ${format.toUpperCase()} format - coming soon!`)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial Reports"
        subtitle="Generate and export monthly financial reports"
      />

      {/* Controls */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <Select
            label="Month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            options={MONTHS}
          />
          <Select
            label="Year"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            options={YEARS}
          />
          <Select
            label="Format"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            options={[
              { value: 'pdf', label: 'PDF' },
              { value: 'csv', label: 'CSV' },
            ]}
          />
          <Button onClick={handleExport} className="w-full sm:w-auto">
            <Download className="h-4 w-4" />
            Export Report
          </Button>
        </div>
      </Card>

      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <div className="space-y-6">
          {/* Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <FileText className="h-5 w-5 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Income</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(summary?.income_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                  <FileText className="h-5 w-5 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Expense</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(summary?.expense_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
            <Card padding="md">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total Savings</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(summary?.savings_total || 0)}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <IncomeVsExpenseChart data={chartData} loading={false} />
            <ExpensePieChart data={[]} loading={true} />
          </div>

          {/* Export Options */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card
              padding="md"
              hover
              onClick={() => { setFormat('pdf'); handleExport(); }}
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-xl">
                  <FileText className="h-6 w-6 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100">Export as PDF</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Download a formatted PDF report</p>
                </div>
              </div>
            </Card>
            <Card
              padding="md"
              hover
              onClick={() => { setFormat('csv'); handleExport(); }}
            >
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                  <FileSpreadsheet className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-gray-100">Export as CSV</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Download data as spreadsheet</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}

