import { Search, X } from 'lucide-react'
import { Input } from './Input'

interface SearchBoxProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function SearchBox({
  value,
  onChange,
  placeholder = 'Search...',
  className = '',
}: SearchBoxProps) {
  return (
    <div className={className}>
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        leftIcon={<Search className="h-4 w-4" />}
        rightIcon={
          value ? (
            <button
              onClick={() => onChange('')}
              className="p-0.5 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          ) : undefined
        }
        className="max-w-sm"
      />
    </div>
  )
}
