import { useState, useMemo } from 'react'
import {
  TrendingUp,
  Search,
  CheckCircle,
  Info,
  Clock,
  Sparkles,
  ShieldCheck,
} from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import {
  useSearchMutualFunds,
  useMutualFundHistory,
  useMutualFundsList,
} from '@/hooks/useAI'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { useTheme } from '@/contexts/ThemeContext'

interface PresetScheme {
  code: number
  name: string
  category: string
}

const POPULAR_SCHEMES_SHORTCUTS: PresetScheme[] = [
  { code: 122639, name: 'Parag Parikh Flexi Cap (Direct)', category: 'Flexi Cap' },
  { code: 120503, name: 'Mirae Asset Large Cap (Direct)', category: 'Large Cap' },
  { code: 120847, name: 'HDFC Mid-Cap Opportunities (Direct)', category: 'Mid Cap' },
  { code: 125354, name: 'Axis Small Cap (Direct)', category: 'Small Cap' },
  { code: 120716, name: 'UTI Nifty 50 Index (Direct)', category: 'Index' },
  { code: 119598, name: 'SBI Bluechip (Direct)', category: 'Large Cap' },
]

const CATEGORIES = [
  'All',
  'Flexi Cap',
  'Large Cap',
  'Mid Cap',
  'Small Cap',
  'Index',
  'ELSS',
  'Hybrid',
  'Debt',
]

const PERIOD_OPTIONS = [
  { label: '1M', value: '1m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
  { label: '3Y', value: '3y' },
  { label: '5Y', value: '5y' },
  { label: 'ALL', value: 'all' },
]

export function MutualFundPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [selectedSchemeCode, setSelectedSchemeCode] = useState<number>(122639) // Default: Parag Parikh Flexi Cap
  const [activeCategory, setActiveCategory] = useState('All')
  const [selectedPeriod, setSelectedPeriod] = useState('1y')

  const { currentTheme } = useTheme()
  const isDark = currentTheme === 'dark'

  // Debounce search query
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setSearchQuery(val)
    const timer = setTimeout(() => {
      setDebouncedQuery(val.trim())
    }, 400)
    return () => clearTimeout(timer)
  }

  // Fetch search results when search query is entered (minimum 2 characters)
  const {
    data: searchResults,
    isLoading: isSearching,
  } = useSearchMutualFunds(debouncedQuery, activeCategory === 'All' ? '' : activeCategory, 25)

  // Fetch popular list from backend
  const { data: popularFunds } = useMutualFundsList()

  // Fetch history and comprehensive metrics for selected scheme code
  const {
    data: fund,
    isLoading: isHistoryLoading,
    isError: isHistoryError,
    refetch: refetchHistory,
  } = useMutualFundHistory(selectedSchemeCode, selectedPeriod)

  // Filter popular schemes based on category
  const filteredPopular = useMemo(() => {
    const rawList = popularFunds?.funds || []
    const baseList: PresetScheme[] = rawList.length > 0
      ? rawList.map((f) => ({
          code: Number(f.scheme_code || f.key || 122639),
          name: f.name,
          category: f.category,
        }))
      : POPULAR_SCHEMES_SHORTCUTS

    if (activeCategory === 'All') return baseList
    return baseList.filter((f) =>
      f.category.toLowerCase().includes(activeCategory.toLowerCase())
    )
  }, [popularFunds, activeCategory])

  const chartData = fund?.chart_data || []
  const chartMinNAV = useMemo(() => {
    if (!chartData.length) return 0
    const min = Math.min(...chartData.map((d) => d.nav))
    return Math.floor(min * 0.97)
  }, [chartData])

  const chartMaxNAV = useMemo(() => {
    if (!chartData.length) return 100
    const max = Math.max(...chartData.map((d) => d.nav))
    return Math.ceil(max * 1.03)
  }, [chartData])

  const periodReturn = fund?.percentage_return ?? 0
  const isPositivePeriod = periodReturn >= 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mutual Fund Analysis"
        subtitle="Real-time AMFI NAV analytics, returns, historical CAGR, and fund comparisons"
      />

      {/* Search & Selection Section */}
      <Card>
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search by scheme name, AMC (e.g. Parag Parikh, HDFC, SBI), or scheme code..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
            />
            {isSearching && (
              <div className="absolute right-3.5 top-1/2 -translate-y-1/2">
                <LoadingSpinner size="sm" />
              </div>
            )}
          </div>

          {/* Search Dropdown / Live Results */}
          {debouncedQuery.length >= 2 && searchResults && (
            <div className="max-h-60 overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 p-2 space-y-1">
              {searchResults.results.length === 0 ? (
                <p className="text-xs text-gray-500 dark:text-gray-400 p-2 text-center">
                  No mutual funds found matching "{debouncedQuery}". Try another keyword or AMC.
                </p>
              ) : (
                searchResults.results.slice(0, 15).map((item) => (
                  <button
                    key={item.scheme_code}
                    onClick={() => {
                      setSelectedSchemeCode(item.scheme_code)
                      setSearchQuery('')
                      setDebouncedQuery('')
                    }}
                    className={`w-full text-left p-2.5 rounded-lg text-xs transition-colors flex items-center justify-between ${
                      selectedSchemeCode === item.scheme_code
                        ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700/60 text-gray-800 dark:text-gray-200'
                    }`}
                  >
                    <div className="pr-4 truncate">
                      <span className="font-semibold">{item.scheme_name}</span>
                      <span className="text-gray-400 dark:text-gray-500 ml-2">
                        Code: {item.scheme_code}
                      </span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                      Select
                    </span>
                  </button>
                ))
              )}
            </div>
          )}

          {/* Category Chips */}
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Browse Categories:
            </p>
            <div className="flex flex-wrap gap-1.5">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1 text-xs rounded-lg font-medium transition-colors ${
                    activeCategory === cat
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Popular Curated Schemes */}
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Popular Direct Schemes:
            </p>
            <div className="flex flex-wrap gap-2">
              {filteredPopular.map((f) => {
                const isSelected = selectedSchemeCode === f.code
                return (
                  <button
                    key={f.code}
                    onClick={() => setSelectedSchemeCode(f.code)}
                    className={`px-3 py-1.5 text-xs rounded-xl border transition-all ${
                      isSelected
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-semibold shadow-xs'
                        : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    {f.name}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </Card>

      {/* Loading & Error States */}
      {isHistoryLoading && (
        <div className="py-12 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      )}

      {isHistoryError && (
        <ErrorMessage
          title="Failed to fetch mutual fund data"
          message="Could not connect to AMFI / MFapi provider for this scheme. Please try another scheme code or retry."
          onRetry={refetchHistory}
        />
      )}

      {fund && fund.available && (
        <>
          {/* Header Card: Scheme Overview */}
          <Card>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                    {fund.plan || 'Direct'}
                  </span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                    {fund.scheme_category || 'Equity'}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    Scheme Code: {fund.scheme_code}
                  </span>
                </div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {fund.scheme_name}
                </h2>
                <p className="text-xs md:text-sm text-gray-500 dark:text-gray-400">
                  Fund House: <span className="font-medium text-gray-700 dark:text-gray-300">{fund.fund_house || 'AMFI Mutual Fund'}</span>
                </p>
              </div>

              {/* Latest NAV Box */}
              <div className="flex flex-col items-start md:items-end bg-gray-50 dark:bg-gray-800/80 p-4 rounded-xl border border-gray-100 dark:border-gray-700/60 min-w-[200px]">
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                  Latest Net Asset Value (NAV)
                </p>
                <div className="text-2xl md:text-3xl font-extrabold text-gray-900 dark:text-gray-100 mt-1">
                  ₹{fund.latest_nav.toFixed(4)}
                </div>
                <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  As of: {fund.nav_date || 'Latest AMFI NAV'}
                </p>
              </div>
            </div>
          </Card>

          {/* Historical Returns & Key Risk Analytics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">1 Month</p>
              <p
                className={`text-lg font-bold mt-1 flex items-center ${
                  (fund.returns_1m ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {fund.returns_1m != null ? `${fund.returns_1m >= 0 ? '+' : ''}${fund.returns_1m.toFixed(2)}%` : 'N/A'}
              </p>
            </Card>

            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">6 Months</p>
              <p
                className={`text-lg font-bold mt-1 flex items-center ${
                  (fund.returns_6m ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {fund.returns_6m != null ? `${fund.returns_6m >= 0 ? '+' : ''}${fund.returns_6m.toFixed(2)}%` : 'N/A'}
              </p>
            </Card>

            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">1 Year Return</p>
              <p
                className={`text-lg font-bold mt-1 flex items-center ${
                  (fund.returns_1y ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {fund.returns_1y != null ? `${fund.returns_1y >= 0 ? '+' : ''}${fund.returns_1y.toFixed(2)}%` : 'N/A'}
              </p>
            </Card>

            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">3Y CAGR</p>
              <p
                className={`text-lg font-bold mt-1 flex items-center ${
                  (fund.cagr_3y ?? fund.returns_3y ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {fund.cagr_3y != null
                  ? `${fund.cagr_3y >= 0 ? '+' : ''}${fund.cagr_3y.toFixed(2)}%`
                  : fund.returns_3y != null
                  ? `${fund.returns_3y >= 0 ? '+' : ''}${fund.returns_3y.toFixed(2)}%`
                  : 'N/A'}
              </p>
            </Card>

            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">5Y CAGR</p>
              <p
                className={`text-lg font-bold mt-1 flex items-center ${
                  (fund.cagr_5y ?? fund.returns_5y ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {fund.cagr_5y != null
                  ? `${fund.cagr_5y >= 0 ? '+' : ''}${fund.cagr_5y.toFixed(2)}%`
                  : fund.returns_5y != null
                  ? `${fund.returns_5y >= 0 ? '+' : ''}${fund.returns_5y.toFixed(2)}%`
                  : 'N/A'}
              </p>
            </Card>

            <Card padding="sm">
              <p className="text-xs text-gray-500 dark:text-gray-400">Sharpe Ratio</p>
              <p className="text-lg font-bold text-gray-900 dark:text-gray-100 mt-1">
                {fund.sharpe_ratio.toFixed(2)}
              </p>
            </Card>
          </div>

          {/* Interactive Historical NAV Chart */}
          <Card>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-gray-100 dark:border-gray-800 gap-3">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary-500" />
                  Historical NAV Chart & Performance
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {fund.selected_period.toUpperCase()} return:{' '}
                  <span
                    className={`font-semibold ${
                      isPositivePeriod ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {isPositivePeriod ? '+' : ''}
                    {periodReturn.toFixed(2)}%
                  </span>
                  {fund.cagr != null && (
                    <span className="ml-1 text-gray-500">
                      (CAGR: {fund.cagr >= 0 ? '+' : ''}{fund.cagr.toFixed(2)}%)
                    </span>
                  )}
                  {fund.start_date && fund.end_date && (
                    <span className="ml-2 text-gray-400">
                      ({fund.start_date} → {fund.end_date})
                    </span>
                  )}
                </p>
              </div>

              {/* Period Filter Buttons */}
              <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-xl">
                {PERIOD_OPTIONS.map((p) => (
                  <button
                    key={p.value}
                    onClick={() => setSelectedPeriod(p.value)}
                    className={`px-3 py-1 text-xs rounded-lg font-semibold transition-all ${
                      selectedPeriod === p.value
                        ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-300 shadow-xs'
                        : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Chart Container */}
            <div className="pt-4 h-72 w-full">
              {chartData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                  No historical NAV data points available for {selectedPeriod.toUpperCase()}
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={chartData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="navGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop
                          offset="5%"
                          stopColor={isPositivePeriod ? '#10b981' : '#ef4444'}
                          stopOpacity={0.3}
                        />
                        <stop
                          offset="95%"
                          stopColor={isPositivePeriod ? '#10b981' : '#ef4444'}
                          stopOpacity={0.0}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke={isDark ? '#374151' : '#e5e7eb'}
                      vertical={false}
                    />
                    <XAxis
                      dataKey="date"
                      stroke={isDark ? '#9ca3af' : '#6b7280'}
                      fontSize={11}
                      tickLine={false}
                      minTickGap={35}
                    />
                    <YAxis
                      stroke={isDark ? '#9ca3af' : '#6b7280'}
                      fontSize={11}
                      tickLine={false}
                      domain={[chartMinNAV, chartMaxNAV]}
                      tickFormatter={(val) => `₹${val}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#1f2937' : '#ffffff',
                        borderColor: isDark ? '#374151' : '#e5e7eb',
                        borderRadius: '0.75rem',
                        fontSize: '0.825rem',
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                      }}
                      formatter={(val: number) => [`₹${val.toFixed(4)}`, 'NAV']}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="nav"
                      stroke={isPositivePeriod ? '#10b981' : '#ef4444'}
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#navGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </Card>

          {/* Additional Fund Characteristics & Pros/Cons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary-500" />
                Fund Attributes & Risk Profile
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Recommendation</span>
                  <span
                    className={`font-semibold px-2 py-0.5 rounded-md text-xs ${
                      fund.recommendation === 'Buy'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : fund.recommendation === 'Hold'
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                    }`}
                  >
                    {fund.recommendation}
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Volatility (Annualized)</span>
                  <span className="font-semibold text-gray-900 dark:text-gray-100">
                    {fund.volatility.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Maximum Drawdown</span>
                  <span className="font-semibold text-red-500">
                    -{fund.max_drawdown.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-gray-100 dark:border-gray-800 text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Scheme Type / Plan</span>
                  <span className="font-semibold text-gray-900 dark:text-gray-100">
                    {fund.scheme_type || 'Open Ended'} ({fund.plan} - {fund.option})
                  </span>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-amber-500" />
                AI Analysis & Insights
              </h3>
              <div className="space-y-2.5">
                {fund.reason && (
                  <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-3">
                    {fund.reason}
                  </p>
                )}
                {fund.pros && fund.pros.length > 0 ? (
                  fund.pros.map((pro: string, i: number) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 text-xs text-gray-700 dark:text-gray-300"
                    >
                      <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>{pro}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-gray-500">No specific highlights listed.</p>
                )}
                {fund.cons && fund.cons.length > 0 && (
                  <div className="pt-2">
                    <p className="text-xs font-semibold text-gray-500 mb-1.5">Considerations:</p>
                    {fund.cons.map((con: string, i: number) => (
                      <div
                        key={i}
                        className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400 mb-1"
                      >
                        <Info className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                        <span>{con}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Regulatory Disclaimer */}
          <Card padding="sm">
            <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-[11px]">
              <Info className="h-4 w-4 text-blue-500 flex-shrink-0" />
              <span>
                <strong>Statutory Notice:</strong> {fund.disclaimer || 'Mutual fund investments are subject to market risks. Read all scheme related documents carefully. Historical NAV returns and CAGR calculations are based on official AMFI disclosures and do not guarantee future returns.'}
              </span>
            </div>
          </Card>
        </>
      )}

      {fund && !fund.available && (
        <ErrorMessage
          title="Scheme data unavailable"
          message={fund.message || 'Unable to retrieve historical NAV records for this scheme.'}
        />
      )}
    </div>
  )
}
