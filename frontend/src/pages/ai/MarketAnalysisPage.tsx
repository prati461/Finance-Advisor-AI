import { useState } from 'react'
import { motion } from 'framer-motion'
import { LineChart as LineChartIcon, TrendingUp, TrendingDown, Activity, Search, Calendar, DollarSign, Award } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useMarketAnalysis, useSymbols } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'
import {
  AreaChart,
  Area,
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

interface SuggestedSymbol {
  symbol: string
  label: string
}

const SUGGESTED_SYMBOLS: SuggestedSymbol[] = [
  { symbol: '^NSEI', label: 'Nifty 50' },
  { symbol: '^BSESN', label: 'Sensex' },
  { symbol: '^NSEBANK', label: 'Bank Nifty' },
  { symbol: 'RELIANCE.NS', label: 'Reliance' },
  { symbol: 'TCS.NS', label: 'TCS' },
  { symbol: 'INFY.NS', label: 'Infosys' },
  { symbol: 'GC=F', label: 'Gold' },
  { symbol: 'SI=F', label: 'Silver' },
]

export function MarketAnalysisPage() {
  const [symbol, setSymbol] = useState('')
  const analysisMutation = useMarketAnalysis()
  const { data: symbolsData } = useSymbols()
  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  const validateSymbol = (sym: string): boolean => {
    const trimmed = sym.trim().toUpperCase()
    if (trimmed.length < 1 || trimmed.length > 30) {
      return false
    }
    // Allow alphanumeric, caret, equals, dots, spaces, hyphens, and ampersands
    if (!/^[\^A-Z0-9=.\s&-]+$/.test(trimmed)) {
      return false
    }
    return true
  }

  const handleAnalyze = (targetSymbol?: string) => {
    const sym = (targetSymbol || symbol).trim().toUpperCase()
    if (validateSymbol(sym)) {
      analysisMutation.mutate(
        { symbol: sym },
        {
          onSuccess: () => {
            setSymbol('')
          },
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

  const priceData = analysis?.historical_data || []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Analysis"
        subtitle="Historical OHLCV analysis of Indian indices, top equities, and global commodities"
      />

      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Enter symbol or name (^NSEI, ^BSESN, RELIANCE, GC=F, SI=F...)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && isSymbolValid && handleAnalyze()}
            />
            {symbol && !isSymbolValid && (
              <p className="text-xs text-red-500 dark:text-red-400 mt-1">
                Symbol must be 1-30 characters (letters, numbers, ^, =, ., or spaces)
              </p>
            )}
          </div>
          <Button
            onClick={() => handleAnalyze()}
            isLoading={analysisMutation.isPending}
            disabled={!isSymbolValid}
          >
            <Search className="h-4 w-4" />
            Analyze
          </Button>
        </div>

        {/* Suggested Quick Buttons */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 mr-1">Popular:</span>
          {SUGGESTED_SYMBOLS.map((s) => (
            <button
              key={s.symbol}
              onClick={() => handleAnalyze(s.symbol)}
              className="px-3 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700/60 text-gray-700 dark:text-gray-300 hover:bg-primary-100 hover:text-primary-700 dark:hover:bg-primary-900/40 dark:hover:text-primary-400 transition-colors border border-transparent hover:border-primary-300 dark:hover:border-primary-700"
            >
              {s.label} ({s.symbol})
            </button>
          ))}
        </div>

        {/* Catalog Chips */}
        {symbolsData && symbolsData.symbols.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex flex-wrap gap-1.5 items-center">
            <span className="text-[11px] text-gray-400 dark:text-gray-500 mr-1">All Assets:</span>
            {symbolsData.symbols.slice(0, 14).map((sym) => (
              <button
                key={sym.key}
                onClick={() => handleAnalyze(sym.symbol)}
                className="px-2 py-0.5 text-[11px] font-medium rounded bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 border border-gray-200 dark:border-gray-700 transition-colors"
                title={sym.name}
              >
                {sym.key}
              </button>
            ))}
          </div>
        )}
      </Card>

      {analysisMutation.isError && (
        <ErrorMessage
          title="Analysis failed"
          message="Unable to analyze this symbol. Please verify the symbol and try again."
          onRetry={() => handleAnalyze()}
        />
      )}

      {analysisMutation.isPending && (
        <div className="py-12 flex justify-center">
          <LoadingSpinner />
        </div>
      )}

      {analysis && analysis.available && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {/* Header Banner */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white dark:bg-gray-800 p-5 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{analysis.name}</h2>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-md bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300">
                  {analysis.symbol}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 uppercase">
                  {analysis.asset_class}
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Data Period: {analysis.start_date} to {analysis.end_date} · {analysis.data_points} observations
              </p>
            </div>

            {/* Technical Signal Badge */}
            {analysis.technical?.signal && (
              <div
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold ${
                  analysis.technical.signal === 'Buy'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : analysis.technical.signal === 'Sell'
                    ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                    : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                }`}
              >
                {analysis.technical.signal === 'Buy' ? (
                  <TrendingUp className="h-5 w-5 text-green-600" />
                ) : analysis.technical.signal === 'Sell' ? (
                  <TrendingDown className="h-5 w-5 text-red-600" />
                ) : (
                  <Activity className="h-5 w-5 text-yellow-600" />
                )}
                <span>Signal: {analysis.technical.signal}</span>
                <span className="text-xs font-normal opacity-80">({analysis.technical.trend || 'Neutral'})</span>
              </div>
            )}
          </div>

          {/* Primary Key Statistics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Current Price</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {analysis.asset_class === 'commodity' ? `$${analysis.current_price.toLocaleString()}` : formatCurrency(analysis.current_price)}
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">5Y CAGR</p>
              <p className={`text-lg font-bold ${analysis.cagr >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {analysis.cagr >= 0 ? '+' : ''}{analysis.cagr.toFixed(2)}%
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Annual Return</p>
              <p className={`text-lg font-bold ${analysis.annual_return >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {analysis.annual_return >= 0 ? '+' : ''}{analysis.annual_return.toFixed(2)}%
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Annual Volatility</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{analysis.volatility.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Max Drawdown</p>
              <p className="text-lg font-bold text-red-600 dark:text-red-400">-{analysis.max_drawdown.toFixed(2)}%</p>
            </Card>
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{analysis.sharpe_ratio.toFixed(2)}</p>
            </Card>
          </div>

          {/* Secondary Financial & Technical Statistics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">Beta vs Benchmark</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{analysis.beta !== undefined ? analysis.beta.toFixed(2) : '1.00'}</p>
            </Card>
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">RSI (14-Day)</p>
              <p className={`text-sm font-semibold ${(analysis.technical?.rsi || 50) >= 70 ? 'text-red-600' : (analysis.technical?.rsi || 50) <= 30 ? 'text-green-600' : 'text-gray-800 dark:text-gray-200'}`}>
                {analysis.technical?.rsi?.toFixed(1) ?? 'N/A'}
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">52-Week High</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                {analysis.fifty_two_week_high ? formatCurrency(analysis.fifty_two_week_high) : 'N/A'}
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">52-Week Low</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                {analysis.fifty_two_week_low ? formatCurrency(analysis.fifty_two_week_low) : 'N/A'}
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">P/E Ratio</p>
              <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                {analysis.pe_ratio ? analysis.pe_ratio.toFixed(2) : 'N/A'}
              </p>
            </Card>
            <Card padding="sm">
              <p className="text-[11px] text-gray-500 dark:text-gray-400">AI Confidence</p>
              <p className="text-sm font-semibold text-primary-600 dark:text-primary-400">
                {(analysis.confidence_score * 100).toFixed(0)}%
              </p>
            </Card>
          </div>

          {/* Real Historical Price Chart */}
          {priceData.length > 0 && (
            <Card>
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                    <LineChartIcon className="h-5 w-5 text-primary-600" />
                    Historical Price Trend
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Real closing price observations over 5 years
                  </p>
                </div>
              </div>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={priceData}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      minTickGap={40}
                    />
                    <YAxis
                      domain={['auto', 'auto']}
                      tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(val) => Number(val).toLocaleString()}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#1f2937' : '#fff',
                        border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                        borderRadius: '8px',
                        color: isDark ? '#f3f4f6' : '#111827',
                      }}
                      formatter={(value: number) => [`${value.toLocaleString()}`, 'Price']}
                    />
                    <Area
                      type="monotone"
                      dataKey="close"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#priceGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {/* Annual Returns Bar Chart */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Annual Calendar Returns
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Year-over-year performance percentage
            </p>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={annualData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#374151' : '#e5e7eb'} />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: isDark ? '#9ca3af' : '#6b7280', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => `${v}%`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: isDark ? '#1f2937' : '#fff',
                      border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                      borderRadius: '8px',
                      color: isDark ? '#f3f4f6' : '#111827',
                    }}
                    formatter={(value: number) => [`${value}%`, 'Return']}
                  />
                  <Bar dataKey="return" radius={[4, 4, 0, 0]}>
                    {annualData.map((entry, i) => (
                      <Cell key={i} fill={entry.return >= 0 ? '#10b981' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </motion.div>
      )}

      {analysis && !analysis.available && (
        <ErrorMessage
          title="Symbol not available"
          message={analysis.message || 'Unable to fetch historical market data for this symbol.'}
        />
      )}
    </div>
  )
}
