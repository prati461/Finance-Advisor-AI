import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { Button } from '@/components/common/Button'
import { INCOME_CATEGORIES, INCOME_FREQUENCIES } from '@/constants'
import { IncomeCreate, IncomeUpdate } from '@/types'

const incomeSchema = z.object({
  source: z.string().min(1, 'Source is required').max(128, 'Source is too long'),
  category: z.string().min(1, 'Category is required'),
  amount: z.coerce
    .number()
    .positive('Amount must be positive')
    .max(99999999, 'Amount is too large'),
  frequency: z.string().min(1, 'Frequency is required'),
  received_date: z.string()
    .min(1, 'Date is required')
    .refine((date) => new Date(date) <= new Date(), {
      message: 'Date cannot be in the future',
    }),
  description: z.string().max(512, 'Description is too long').optional().nullable(),
})

type IncomeFormData = z.infer<typeof incomeSchema>

interface IncomeFormProps {
  defaultValues?: Partial<IncomeCreate>
  onSubmit: (data: IncomeCreate | IncomeUpdate) => Promise<void> | void
  onCancel: () => void
  isLoading?: boolean
  mode: 'create' | 'edit'
}

export function IncomeForm({
  defaultValues,
  onSubmit,
  onCancel,
  isLoading = false,
  mode,
}: IncomeFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<IncomeFormData>({
    resolver: zodResolver(incomeSchema),
    defaultValues: {
      source: '',
      category: '',
      amount: undefined,
      frequency: '',
      received_date: new Date().toISOString().split('T')[0],
      description: '',
      ...defaultValues,
    },
  })

  const handleFormSubmit = async (data: IncomeFormData) => {
    await onSubmit(data as unknown as IncomeCreate | IncomeUpdate)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Input
        label="Source"
        placeholder="e.g., Salary, Freelance Project"
        error={errors.source?.message}
        {...register('source')}
      />

      <Select
        label="Category"
        options={INCOME_CATEGORIES.map((c) => ({ value: c, label: c }))}
        placeholder="Select category"
        error={errors.category?.message}
        {...register('category')}
      />

      <Input
        label="Amount"
        type="number"
        step="0.01"
        placeholder="0.00"
        error={errors.amount?.message}
        {...register('amount')}
      />

      <Select
        label="Frequency"
        options={INCOME_FREQUENCIES.map((f) => ({ value: f, label: f }))}
        placeholder="Select frequency"
        error={errors.frequency?.message}
        {...register('frequency')}
      />

      <Input
        label="Received Date"
        type="date"
        error={errors.received_date?.message}
        {...register('received_date')}
      />

      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
          Description
        </label>
        <textarea
          className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-colors duration-200"
          rows={3}
          placeholder="Optional description"
          {...register('description')}
        />
        {errors.description?.message && (
          <p className="mt-1.5 text-sm text-red-500">{errors.description.message}</p>
        )}
      </div>

      <div className="flex gap-3 justify-end pt-2">
        <Button variant="secondary" onClick={onCancel} type="button">
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {mode === 'create' ? 'Add Income' : 'Update Income'}
        </Button>
      </div>
    </form>
  )
}
