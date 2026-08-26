import { useState } from 'react'
import { motion } from 'framer-motion'
import { LineChart, TrendingUp, TrendingDown, Activity, DollarSign, BarChart3 } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useStockPrediction } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

const STOCK_SUGGESTIONS = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'WIPRO', 'AXISBANK']

export function StockPredictionPage() {
  const [symbol, setSymbol] = useState('')
  const predictMutation = useStockPrediction()
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  const validateSymbol = (sym: string): boolean => {
    const trimmed = sym.trim().toUpperCase()
    // Symbol should be 1-10 characters, alphanumeric only (for NSE/BSE symbols)
    if (trimmed.length < 1 || trimmed.length > 10) {
      return false
    }
    if (!/^[A-Z0-9&-]+$/.test(trimmed)) {
      return false
    }
    return true
  }

  const handlePredict = () => {
    if (validateSymbol(symbol)) {
      predictMutation.mutate(
        { symbol: symbol.trim().toUpperCase() },
        {
          onSuccess: () => {
            // Clear input after successful prediction
            setSymbol('')
          }
        }
      )
    }
  }

  const prediction = predictMutation.data
  const isSymbolValid = validateSymbol(symbol)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Stock Price Prediction"
        subtitle="AI-powered stock price predictions using trained ML models"
      />

      {/* Search Input */}
      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Enter stock symbol (e.g., RELIANCE, TCS)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && isSymbolValid && handlePredict()}
            />
            {symbol && !isSymbolValid && (
              <p className="text-xs text-red-500 dark:text-red-400 mt-1">
                Symbol must be 1-10 characters (letters, numbers, &, or -)
              </p>
            )}
          </div>
          <Button 
            onClick={handlePredict} 
            isLoading={predictMutation.isPending}
            disabled={!isSymbolValid}
          >
            <LineChart className="h-4 w-4" />
            Predict
          </Button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {STOCK_SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => { 
                setSymbol(s)
                predictMutation.mutate({ symbol: s }, {
                  onSuccess: () => setSymbol('')
                })
              }}
              className="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-primary-100 hover:text-primary-700 dark:hover:bg-primary-900/30 dark:hover:text-primary-400 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      </Card>

      {predictMutation.isError && (
        <ErrorMessage
          title="Prediction failed"
          message="Unable to predict stock price. Please try again."
          onRetry={handlePredict}
        />
      )}

      {predictMutation.isPending && <LoadingSpinner />}

      {prediction && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card padding="sm">
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Symbol</p>
                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{prediction.symbol}</p>
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Current Price</p>
                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {formatCurrency(prediction.current_price)}
                </p>
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Tomorrow</p>
                <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                  {formatCurrency(prediction.tomorrow_price)}
                </p>
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">7 Day Avg</p>
                <p className="text-xl font-bold text-purple-600 dark:text-purple-400">
                  {formatCurrency(prediction.next_7_days_avg)}
                </p>
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-center">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">30 Day Avg</p>
                <p className="text-xl font-bold text-green-600 dark:text-green-400">
                  {formatCurrency(prediction.next_30_days_avg)}
                </p>
              </div>
            </Card>
          </div>

          {/* Trend & Confidence */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card>
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  prediction.trend === 'Upward' ? 'bg-green-100 dark:bg-green-900/30' :
                  prediction.trend === 'Downward' ? 'bg-red-100 dark:bg-red-900/30' :
                  'bg-gray-100 dark:bg-gray-700'
                }`}>
                  {prediction.trend === 'Upward' ? (
                    <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
                  ) : prediction.trend === 'Downward' ? (
                    <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
                  ) : (
                    <Activity className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Trend</p>
                  <p className={`text-lg font-bold ${
                    prediction.trend === 'Upward' ? 'text-green-600 dark:text-green-400' :
                    prediction.trend === 'Downward' ? 'text-red-600 dark:text-red-400' :
                    'text-gray-600 dark:text-gray-400'
                  }`}>{prediction.trend}</p>
                </div>
              </div>
            </Card>
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Confidence Score</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {(prediction.confidence_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Price Chart */}
          {prediction.predictions.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                30-Day Price Forecast
              </h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <ReLineChart data={prediction.predictions}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      interval={4}
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
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                  </ReLineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

