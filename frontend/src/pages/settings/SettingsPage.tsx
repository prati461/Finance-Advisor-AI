import { Sun, Moon, Monitor, Palette, Info, Wallet } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card } from '@/components/common/Card'
import { useTheme } from '@/contexts/ThemeContext'
import { classNames } from '@/utils'

const themeOptions = [
  { value: 'light' as const, label: 'Light', icon: Sun, description: 'Always use light mode' },
  { value: 'dark' as const, label: 'Dark', icon: Moon, description: 'Always use dark mode' },
  { value: 'system' as const, label: 'System', icon: Monitor, description: 'Follow system preference' },
]

export function SettingsPage() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <PageHeader title="Settings" subtitle="Customize your experience" />

      {/* Theme Settings */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Theme
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {themeOptions.map(({ value, label, icon: Icon, description }) => (
            <button
              key={value}
              onClick={() => setTheme(value)}
              className={classNames(
                'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200',
                theme === value
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              )}
            >
              <Icon
                className={classNames(
                  'h-6 w-6',
                  theme === value ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400'
                )}
              />
              <span
                className={classNames(
                  'text-sm font-medium',
                  theme === value
                    ? 'text-primary-700 dark:text-primary-300'
                    : 'text-gray-700 dark:text-gray-300'
                )}
              >
                {label}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 text-center">
                {description}
              </span>
            </button>
          ))}
        </div>
      </Card>

      {/* App Info */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Info className="h-5 w-5" />
          Application Information
        </h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">Application</span>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
              AI-Powered Finance Advisor
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">Version</span>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">1.0.0</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">Frontend</span>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
              React 19 + TypeScript + Tailwind CSS
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Backend</span>
            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
              FastAPI + Python + ML
            </span>
          </div>
        </div>
      </Card>
    </div>
  )
}
