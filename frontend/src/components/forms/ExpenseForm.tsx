import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input } from '@/components/common/Input'
import { Select } from '@/components/common/Select'
import { Button } from '@/components/common/Button'
import { EXPENSE_CATEGORIES } from '@/constants'
import { ExpenseCreate, ExpenseUpdate } from '@/types'

const expenseSchema = z.object({
  category: z.string().min(1, 'Category is required'),
  amount: z.coerce
    .number()
    .positive('Amount must be positive')
    .max(99999999, 'Amount is too large'),
  spent_at: z.string()
    .min(1, 'Date is required')
    .refine((date) => new Date(date) <= new Date(), {
      message: 'Date cannot be in the future',
    }),
  description: z.string().max(512, 'Description is too long').optional().nullable(),
  merchant: z.string().max(128, 'Merchant name is too long').optional().nullable(),
  payment_method: z.string().max(64, 'Payment method is too long').optional().nullable(),
})

type ExpenseFormData = z.infer<typeof expenseSchema>

interface ExpenseFormProps {
  defaultValues?: Partial<ExpenseCreate>
  onSubmit: (data: ExpenseCreate | ExpenseUpdate) => Promise<void> | void
  onCancel: () => void
  isLoading?: boolean
  mode: 'create' | 'edit'
}

export function ExpenseForm({
  defaultValues,
  onSubmit,
  onCancel,
  isLoading = false,
  mode,
}: ExpenseFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ExpenseFormData>({
    resolver: zodResolver(expenseSchema),
    defaultValues: {
      category: '',
      amount: undefined,
      spent_at: new Date().toISOString().split('T')[0],
      description: '',
      merchant: '',
      payment_method: '',
      ...defaultValues,
    },
  })

  const handleFormSubmit = async (data: ExpenseFormData) => {
    await onSubmit(data as unknown as ExpenseCreate | ExpenseUpdate)
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
        label="Amount"
        type="number"
        step="0.01"
        placeholder="0.00"
        error={errors.amount?.message}
        {...register('amount')}
      />

      <Input
        label="Date"
        type="date"
        error={errors.spent_at?.message}
        {...register('spent_at')}
      />

      <Input
        label="Merchant"
        placeholder="e.g., Amazon, Uber"
        error={errors.merchant?.message}
        {...register('merchant')}
      />

      <Input
        label="Payment Method"
        placeholder="e.g., Credit Card, Cash"
        error={errors.payment_method?.message}
        {...register('payment_method')}
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
          {mode === 'create' ? 'Add Expense' : 'Update Expense'}
        </Button>
      </div>
    </form>
  )
}
