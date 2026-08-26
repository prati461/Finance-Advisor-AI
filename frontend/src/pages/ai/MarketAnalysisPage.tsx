import { useState } from 'react'
import { motion } from 'framer-motion'
import { LineChart, TrendingUp, TrendingDown, Activity, Search } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useMarketAnalysis, useSymbols } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

const SUGGESTED = ['^NSEI', '^BSESN', 'NIFTYBANK', 'GC=F', 'SI=F']

export function MarketAnalysisPage() {
  const [symbol, setSymbol] = useState('')
  const analysisMutation = useMarketAnalysis()
  const { data: symbolsData } = useSymbols()
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  const validateSymbol = (sym: string): boolean => {
    const trimmed = sym.trim().toUpperCase()
    // Symbol should be 1-10 characters, with ^, alphanumeric, =
    if (trimmed.length < 1 || trimmed.length > 15) {
      return false
    }
    if (!/^[\^A-Z0-9=.]+$/.test(trimmed)) {
      return false
    }
    return true
  }

  const handleAnalyze = () => {
    if (validateSymbol(symbol)) {
      analysisMutation.mutate(
        { symbol: symbol.trim().toUpperCase() },
        {
          onSuccess: () => {
            // Clear input after successful analysis
            setSymbol('')
          }
        }
      )
    }
  }

  const analysis = analysisMutation.data
  const isSymbolValid = validateSymbol(symbol)

  const annualData = analysis
    ? (analysis.yearly_returns || []).map((item) => ({
        name: String(item.year),
        return: Number(item.return),
      }))
    : []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Analysis"
        subtitle="5-year historical analysis of any index, stock, or commodity"
      />

      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Enter symbol (^NSEI, ^BSESN, RELIANCE, GC=F...)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && isSymbolValid && handleAnalyze()}
            />
            {symbol && !isSymbolValid && (
              <p className="text-xs text-red-500 dark:text-red-400 mt-1">
                Symbol must be 1-15 characters (letters, numbers, ^, =, or .)
              </p>
            )}
          </div>
          <Button 
            onClick={handleAnalyze} 
            isLoading={analysisMutation.isPending}
            disabled={!isSymbolValid}
          >
            <Search className="h-4 w-4" />
            Analyze
          </Button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {SUGGESTED.map((s) => (
            <button
              key={s}
              onClick={() => { 
                setSymbol(s)
                analysisMutation.mutate({ symbol: s }, {
                  onSuccess: () => setSymbol('')
                })
              }}
              className="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-primary-100 hover:text-primary-700 dark:hover:bg-primary-900/30 dark:hover:text-primary-400 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
        {symbolsData && symbolsData.symbols.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {symbolsData.symbols.slice(0, 12).map((sym) => (
              <button
                key={sym.key}
                onClick={() => { 
                  setSymbol(sym.symbol)
                  analysisMutation.mutate({ symbol: sym.symbol }, {
                    onSuccess: () => setSymbol('')
                  })
                }}
                className="px-2 py-0.5 text-[10px] font-medium rounded bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:text-primary-600 border border-gray-200 dark:border-gray-700"
                title={sym.name}
              >
                {sym.key}
              </button>
            ))}
          </div>
        )}
      </Card>

      {analysisMutation.isError && (
        <ErrorMessage title="Analysis failed" message="Unable to analyze this symbol. Please try again." onRetry={handleAnalyze} />
      )}

      {analysisMutation.isPending && <LoadingSpinner />}

      {analysis && analysis.available && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Current Price</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{formatCurrency(analysis.current_price)}</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">5Y CAGR</p>
              <p className={`text-lg font-bold ${analysis.cagr >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>{analysis.cagr.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Volatility</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{analysis.volatility.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Max Drawdown</p>
              <p className="text-lg font-bold text-red-600 dark:text-red-400">{analysis.max_drawdown.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{analysis.sharpe_ratio.toFixed(2)}</p>
            </Card>
<Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">RSI</p>
              <p className={`text-lg font-bold ${(analysis.technical?.rsi || 50) >= 70 ? 'text-red-600' : (analysis.technical?.rsi || 50) <= 30 ? 'text-green-600' : 'text-gray-900 dark:text-gray-100'}`}>{analysis.technical?.rsi?.toFixed(1) ?? 'N/A'}</p>
            </Card>
          </div>

          {/* Signal */}
          {analysis.technical?.signal && (
            <div className={`flex items-center gap-3 p-4 rounded-xl ${
              analysis.technical.signal === 'Buy' ? 'bg-green-50 dark:bg-green-900/20' :
              analysis.technical.signal === 'Sell' ? 'bg-red-50 dark:bg-red-900/20' :
              'bg-yellow-50 dark:bg-yellow-900/20'
            }`}>
              {analysis.technical.signal === 'Buy' ? <TrendingUp className="h-6 w-6 text-green-600" /> : analysis.technical.signal === 'Sell' ? <TrendingDown className="h-6 w-6 text-red-600" /> : <Activity className="h-6 w-6 text-yellow-600" />}
              <div>
                <p className={`text-lg font-bold ${
                  analysis.technical.signal === 'Buy' ? 'text-green-600 dark:text-green-400' :
                  analysis.technical.signal === 'Sell' ? 'text-red-600 dark:text-red-400' : 'text-yellow-600 dark:text-yellow-400'
                }`}>{analysis.technical.signal}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300">Trend: {analysis.technical.trend || 'N/A'}</p>
              </div>
            </div>
          )}

          {/* Annual Returns Bar Chart */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Annual Returns</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={annualData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                  <XAxis dataKey="name" tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
                  <Tooltip contentStyle={{ backgroundColor: isDark ? '#1f2937' : '#fff', border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`, borderRadius: '8px', color: isDark ? '#f3f4f6' : '#111827' }} formatter={(value: number) => [`${value}%`]} />
                  <Bar dataKey="return" radius={[4, 4, 0, 0]}>
                    {annualData.map((entry, i) => (
                      <Cell key={i} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {analysis.message && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{analysis.message}</p>
          )}
        </>
      )}

      {analysis && !analysis.available && (
        <ErrorMessage title="Symbol not available" message={analysis.message || 'Unable to fetch data for this symbol.'} />
      )}
    </div>
  )
}
