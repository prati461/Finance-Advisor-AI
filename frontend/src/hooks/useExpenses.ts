import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { expenseService, ExpenseListParams } from '@/services/expense.service'
import { ExpenseCreate, ExpenseUpdate } from '@/types'
import toast from 'react-hot-toast'
import { QUERY_KEYS } from '@/constants'

export function useExpenses(params?: ExpenseListParams) {
  return useQuery({
    queryKey: [...QUERY_KEYS.expenses, params],
    queryFn: () => expenseService.list(params),
    placeholderData: (prev) => prev,
  })
}

export function useExpense(id: number) {
  return useQuery({
    queryKey: [...QUERY_KEYS.expenses, id],
    queryFn: () => expenseService.getById(id),
    enabled: !!id,
  })
}

export function useCreateExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ExpenseCreate) => expenseService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.expenses })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Expense added successfully')
    },
    onError: () => {
      toast.error('Failed to add expense')
    },
  })
}

export function useUpdateExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ExpenseUpdate }) =>
      expenseService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.expenses })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Expense updated successfully')
    },
    onError: () => {
      toast.error('Failed to update expense')
    },
  })
}

export function useDeleteExpense() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => expenseService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.expenses })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Expense deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete expense')
    },
  })
}
