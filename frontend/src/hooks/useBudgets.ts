import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { budgetService, BudgetListParams } from '@/services/budget.service'
import { BudgetCreate, BudgetUpdate } from '@/types'
import toast from 'react-hot-toast'
import { QUERY_KEYS } from '@/constants'

export function useBudgets(params?: BudgetListParams) {
  return useQuery({
    queryKey: [...QUERY_KEYS.budgets, params],
    queryFn: () => budgetService.list(params),
    placeholderData: (prev) => prev,
  })
}

export function useBudget(id: number) {
  return useQuery({
    queryKey: [...QUERY_KEYS.budgets, id],
    queryFn: () => budgetService.getById(id),
    enabled: !!id,
  })
}

export function useCreateBudget() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: BudgetCreate) => budgetService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.budgets })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Budget created successfully')
    },
    onError: () => {
      toast.error('Failed to create budget')
    },
  })
}

export function useUpdateBudget() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: BudgetUpdate }) =>
      budgetService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.budgets })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Budget updated successfully')
    },
    onError: () => {
      toast.error('Failed to update budget')
    },
  })
}

export function useDeleteBudget() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => budgetService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.budgets })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Budget deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete budget')
    },
  })
}
