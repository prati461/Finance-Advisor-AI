import { useState } from 'react'
import { motion } from 'framer-motion'
import { Home, DollarSign, TrendingUp, Shield, MapPin } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { useHousePricePrediction } from '@/hooks/useAI'
import { formatCurrency } from '@/utils'

const LOCATIONS = [
  'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
  'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow',
]

export function HousePricePage() {
  const [area, setArea] = useState('')
  const [bedrooms, setBedrooms] = useState('')
  const [bathrooms, setBathrooms] = useState('')
  const [location, setLocation] = useState('')

  const predictMutation = useHousePricePrediction()

  const handleInputChange = (
    value: string,
    setter: (val: string) => void,
    min?: number,
    max?: number
  ) => {
    const numValue = parseFloat(value)
    if (!value || isNaN(numValue)) {
      setter('')
      return
    }
    
    let bounded = numValue
    if (min !== undefined) bounded = Math.max(min, bounded)
    if (max !== undefined) bounded = Math.min(max, bounded)
    
    setter(bounded.toString())
  }

  const handlePredict = () => {
    const areaNum = parseFloat(area)
    const bedroomsNum = parseInt(bedrooms)
    const bathroomsNum = parseInt(bathrooms)

    // Validate inputs
    if (!area || !bedrooms || !bathrooms || !location) {
      return
    }
    
    if (areaNum <= 0 || areaNum > 1000000) {
      return
    }
    
    if (bedroomsNum < 1 || bedroomsNum > 10) {
      return
    }
    
    if (bathroomsNum < 1 || bathroomsNum > 10) {
      return
    }

    predictMutation.mutate({
      area: areaNum,
      bedrooms: bedroomsNum,
      bathrooms: bathroomsNum,
      location,
    })
  }

  const prediction = predictMutation.data
  const isValid = area && bedrooms && bathrooms && location

  return (
    <div className="space-y-6">
      <PageHeader
        title="House Price Prediction"
        subtitle="AI-powered house price estimation based on property features"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Property Details
          </h3>
          <div className="space-y-4">
            <div>
              <Input
                label="Area (sq ft)"
                type="number"
                placeholder="e.g., 1500"
                min={1}
                max={1000000}
                value={area}
                onChange={(e) => handleInputChange(e.target.value, setArea, 1, 1000000)}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 1 sq ft, Max: 1,000,000 sq ft</p>
            </div>
            <div>
              <Input
                label="Bedrooms"
                type="number"
                placeholder="e.g., 3"
                min={1}
                max={10}
                value={bedrooms}
                onChange={(e) => handleInputChange(e.target.value, setBedrooms, 1, 10)}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 1, Max: 10</p>
            </div>
            <div>
              <Input
                label="Bathrooms"
                type="number"
                placeholder="e.g., 2"
                min={1}
                max={10}
                value={bathrooms}
                onChange={(e) => handleInputChange(e.target.value, setBathrooms, 1, 10)}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Min: 1, Max: 10</p>
            </div>
            <Select
              label="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              options={[
                { value: '', label: 'Select location' },
                ...LOCATIONS.map(loc => ({ value: loc, label: loc })),
              ]}
            />
            <Button
              className="w-full"
              onClick={handlePredict}
              disabled={!isValid}
              isLoading={predictMutation.isPending}
            >
              <Home className="h-4 w-4" />
              Predict Price
            </Button>
          </div>
        </Card>

        {/* Results */}
        <div className="space-y-4">
          {predictMutation.isError && (
            <ErrorMessage
              title="Prediction failed"
              message="Unable to predict house price. Please try again."
              onRetry={handlePredict}
            />
          )}

          {predictMutation.isPending && <LoadingSpinner />}

          {prediction && (
            <>
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Estimated Price
                </h3>
                <div className="text-center py-6">
                  <motion.p
                    initial={{ scale: 0.5, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.5, type: 'spring' }}
                    className="text-4xl font-bold text-primary-600 dark:text-primary-400"
                  >
                    {formatCurrency(prediction.predicted_price)}
                  </motion.p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    Estimated price range: {formatCurrency(prediction.price_range_low)} - {formatCurrency(prediction.price_range_high)}
                  </p>
                </div>
              </Card>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card padding="sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                      <Shield className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Investment Rating</p>
                      <p className="text-sm font-bold text-gray-900 dark:text-gray-100">
                        {prediction.investment_rating}
                      </p>
                    </div>
                  </div>
                </Card>
                <Card padding="sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Confidence</p>
                      <p className="text-sm font-bold text-gray-900 dark:text-gray-100">
                        {(prediction.confidence_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </Card>
              </div>

              <Card padding="sm">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <MapPin className="h-4 w-4" />
                  <span>{location} · {bedrooms} BHK · {area} sq ft</span>
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

