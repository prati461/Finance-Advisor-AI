import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { incomeService, IncomeListParams } from '@/services/income.service'
import { IncomeCreate, IncomeUpdate } from '@/types'
import toast from 'react-hot-toast'
import { QUERY_KEYS } from '@/constants'

export function useIncomes(params?: IncomeListParams) {
  return useQuery({
    queryKey: [...QUERY_KEYS.incomes, params],
    queryFn: () => incomeService.list(params),
    placeholderData: (prev) => prev,
  })
}

export function useIncome(id: number) {
  return useQuery({
    queryKey: [...QUERY_KEYS.incomes, id],
    queryFn: () => incomeService.getById(id),
    enabled: !!id,
  })
}

export function useCreateIncome() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: IncomeCreate) => incomeService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.incomes })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Income added successfully')
    },
    onError: () => {
      toast.error('Failed to add income')
    },
  })
}

export function useUpdateIncome() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: IncomeUpdate }) =>
      incomeService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.incomes })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Income updated successfully')
    },
    onError: () => {
      toast.error('Failed to update income')
    },
  })
}

export function useDeleteIncome() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => incomeService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.incomes })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.summary })
      toast.success('Income deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete income')
    },
  })
}
