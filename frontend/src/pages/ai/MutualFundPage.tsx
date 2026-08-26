import { useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Shield, DollarSign, PieChart, Info, CheckCircle, XCircle } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useMutualFundAnalysis, useMutualFundsList } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'

export function MutualFundPage() {
  const [selected, setSelected] = useState('')
  const { data: fundsList, isLoading: listLoading } = useMutualFundsList()
  const analysisMutation = useMutualFundAnalysis()

  const handleAnalyze = () => {
    if (selected) {
      analysisMutation.mutate({ fund: selected })
    }
  }

  const fund = analysisMutation.data
  const fundOptions = (fundsList?.funds || []).map((f) => ({
    value: f.key,
    label: `${f.name} (${f.category})`,
  }))

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mutual Fund Analysis"
        subtitle="Analyze mutual funds with AI-powered recommendations"
      />

      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
<div className="flex-1">
            <Select
              placeholder={listLoading ? 'Loading funds...' : 'Select a mutual fund...'}
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              options={fundOptions}
              disabled={listLoading}
            />
          </div>
          <Button onClick={handleAnalyze} isLoading={analysisMutation.isPending}>
            <TrendingUp className="h-4 w-4" />
            Analyze
          </Button>
        </div>
      </Card>

      {analysisMutation.isError && (
        <ErrorMessage title="Analysis failed" message="Unable to analyze this fund." onRetry={handleAnalyze} />
      )}

      {analysisMutation.isPending && <LoadingSpinner />}

      {fund && fund.available && (
        <>
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">{fund.name}</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">{fund.category} · {fund.fund_manager}</p>
            </div>
            <div className={`px-4 py-2 rounded-xl text-sm font-bold ${
              fund.recommendation === 'Buy' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
              fund.recommendation === 'Hold' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
              'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
            }`}>{fund.recommendation}</div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">1Y Return</p>
              <p className={`text-lg font-bold ${fund.returns_1y >= 0 ? 'text-green-600' : 'text-red-600'}`}>{fund.returns_1y.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">3Y Return</p>
              <p className={`text-lg font-bold ${fund.returns_3y >= 0 ? 'text-green-600' : 'text-red-600'}`}>{fund.returns_3y.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">5Y CAGR</p>
              <p className={`text-lg font-bold ${fund.cagr_5y >= 0 ? 'text-green-600' : 'text-red-600'}`}>{fund.cagr_5y.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Expense Ratio</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{fund.expense_ratio.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">AUM</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{formatCurrency(fund.aum_estimate)}</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Risk Level</p>
              <p className={`text-lg font-bold ${
                fund.risk_level === 'High' ? 'text-red-600' :
                fund.risk_level === 'Moderate' ? 'text-yellow-600' : 'text-green-600'
              }`}>{fund.risk_level}</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Volatility</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{fund.volatility.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{fund.sharpe_ratio.toFixed(2)}</p>
            </Card>
          </div>

          {/* Pros & Cons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card>
              <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-3 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" /> Pros
              </h3>
              <ul className="space-y-2">
                {fund.pros.map((pro, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-green-500 flex-shrink-0" />
                    {pro}
                  </li>
                ))}
              </ul>
            </Card>
            <Card>
              <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-3 flex items-center gap-2">
                <XCircle className="h-5 w-5" /> Cons
              </h3>
              <ul className="space-y-2">
                {fund.cons.map((con, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-red-500 flex-shrink-0" />
                    {con}
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          {/* Reason */}
          <Card>
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">AI Recommendation</h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">{fund.reason}</p>
              </div>
            </div>
          </Card>
        </>
      )}

      {fund && !fund.available && (
        <ErrorMessage title="Fund not available" message={fund.message || 'Unable to analyze this fund.'} />
      )}
    </div>
  )
}
