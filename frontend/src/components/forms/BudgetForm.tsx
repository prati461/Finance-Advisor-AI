import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { Button } from '@/components/common/Button'
import { EXPENSE_CATEGORIES } from '@/constants'
import { BudgetCreate, BudgetUpdate } from '@/types'

const budgetSchema = z.object({
  category: z.string().min(1, 'Category is required'),
  budget_amount: z.coerce
    .number()
    .positive('Budget amount must be positive')
    .max(99999999, 'Budget amount is too large'),
  month: z.coerce.number().min(1, 'Invalid month').max(12, 'Invalid month'),
  year: z.coerce.number().min(2000, 'Invalid year').max(2100, 'Invalid year'),
  alert_threshold_pct: z.coerce.number().min(0, 'Min 0%').max(100, 'Max 100%'),
})

type BudgetFormData = z.infer<typeof budgetSchema>

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

interface BudgetFormProps {
  defaultValues?: Partial<BudgetCreate>
  onSubmit: (data: BudgetCreate | BudgetUpdate) => Promise<void> | void
  onCancel: () => void
  isLoading?: boolean
  mode: 'create' | 'edit'
}

export function BudgetForm({
  defaultValues,
  onSubmit,
  onCancel,
  isLoading = false,
  mode,
}: BudgetFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BudgetFormData>({
    resolver: zodResolver(budgetSchema),
    defaultValues: {
      category: '',
      budget_amount: undefined,
      month: currentMonth,
      year: currentYear,
      alert_threshold_pct: 80,
      ...defaultValues,
    },
  })

  const handleFormSubmit = async (data: BudgetFormData) => {
    await onSubmit(data as unknown as BudgetCreate | BudgetUpdate)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Select
        label="Category"
        options={EXPENSE_CATEGORIES.map((c) => ({ value: c, label: c }))}
        placeholder="Select category"
        error={errors.category?.message}
        {...register('category')}
      />

      <Input
        label="Budget Amount"
        type="number"
        step="0.01"
        placeholder="0.00"
        error={errors.budget_amount?.message}
        {...register('budget_amount')}
      />

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Month"
          type="number"
          min={1}
          max={12}
          placeholder="1-12"
          error={errors.month?.message}
          {...register('month')}
        />
        <Input
          label="Year"
          type="number"
          min={2000}
          max={2100}
          placeholder="2024"
          error={errors.year?.message}
          {...register('year')}
        />
      </div>

      <Input
        label="Alert Threshold (%)"
        type="number"
        min={0}
        max={100}
        placeholder="80"
        error={errors.alert_threshold_pct?.message}
        {...register('alert_threshold_pct')}
      />

      <div className="flex gap-3 justify-end pt-2">
        <Button variant="secondary" onClick={onCancel} type="button">
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading}>
          {mode === 'create' ? 'Create Budget' : 'Update Budget'}
        </Button>
      </div>
    </form>
  )
}
