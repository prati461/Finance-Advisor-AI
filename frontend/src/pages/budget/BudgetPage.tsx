import { useState, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, Pencil, Trash2, PiggyBank, Target } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Modal } from '@/components/common/Modal'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Badge } from '@/components/common/Badge'
import { EmptyState } from '@/components/common/EmptyState'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { CardSkeleton } from '@/components/common/Skeleton'
import { BudgetForm } from '@/components/forms/BudgetForm'
import { useBudgets, useCreateBudget, useUpdateBudget, useDeleteBudget } from '@/hooks/useBudgets'
import { useExpenses } from '@/hooks/useExpenses'
import { formatCurrency, getCurrentMonth, getCurrentYear, getMonthName } from '@/utils'
import { EXPENSE_CATEGORY_COLORS } from '@/constants'
import { BudgetCreate, BudgetUpdate, BudgetRead } from '@/types'

const currentMonth = getCurrentMonth()
const currentYear = getCurrentYear()

export function BudgetPage() {
  const [searchParams] = useSearchParams()
  const [showModal, setShowModal] = useState(searchParams.get('add') === 'true')
  const [editingBudget, setEditingBudget] = useState<BudgetRead | null>(null)
  const [deletingBudget, setDeletingBudget] = useState<BudgetRead | null>(null)

  const { data, isLoading, error, refetch } = useBudgets({
    month: currentMonth,
    year: currentYear,
  })
  const { data: expensesData } = useExpenses({ page: 1, page_size: 100 })

  const createMutation = useCreateBudget()
  const updateMutation = useUpdateBudget()
  const deleteMutation = useDeleteBudget()

  const expenseByCategory = useMemo(() => {
    if (!expensesData?.items) return {}
    const map: Record<string, number> = {}
    expensesData.items.forEach((e) => {
      map[e.category] = (map[e.category] || 0) + e.amount
    })
    return map
  }, [expensesData])

  const handleCreate = async (formData: BudgetCreate | BudgetUpdate) => {
    await createMutation.mutateAsync(formData as BudgetCreate)
    setShowModal(false)
  }

  const handleUpdate = async (formData: BudgetCreate | BudgetUpdate) => {
    if (!editingBudget) return
    await updateMutation.mutateAsync({ id: editingBudget.id, data: formData as BudgetUpdate })
    setEditingBudget(null)
  }

  const handleDelete = async () => {
    if (!deletingBudget) return
    await deleteMutation.mutateAsync(deletingBudget.id)
    setDeletingBudget(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Budgets"
        subtitle={`${getMonthName(currentMonth)} ${currentYear}`}
        action={
          <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
            Create Budget
          </Button>
        }
      />

      {error ? (
        <ErrorMessage onRetry={refetch} />
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : !data?.items?.length ? (
        <EmptyState
          icon={<Target className="h-12 w-12" />}
          title="No budgets set"
          description="Create your first budget to start tracking spending limits"
          action={
            <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
              Create Budget
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((budget, index) => {
            const spent = expenseByCategory[budget.category] || 0
            const percentage = budget.budget_amount > 0 ? (spent / budget.budget_amount) * 100 : 0
            const remaining = budget.budget_amount - spent
            const isOverBudget = percentage > 100
            const isWarning = percentage >= budget.alert_threshold_pct && !isOverBudget

            return (
              <motion.div
                key={budget.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card padding="md" className="relative overflow-hidden">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div
                        className="p-2.5 rounded-lg"
                        style={{
                          backgroundColor: `${EXPENSE_CATEGORY_COLORS[budget.category]}20`,
                        }}
                      >
                        <PiggyBank
                          className="h-5 w-5"
                          style={{ color: EXPENSE_CATEGORY_COLORS[budget.category] }}
                        />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                          {budget.category}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {getMonthName(budget.month)} {budget.year}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingBudget(budget)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDeletingBudget(budget)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-gray-600 dark:text-gray-400">
                        {formatCurrency(spent)} spent
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        of {formatCurrency(budget.budget_amount)}
                      </span>
                    </div>
                    <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(percentage, 100)}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className={`h-full rounded-full transition-all ${
                          isOverBudget
                            ? 'bg-red-500'
                            : isWarning
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        }`}
                      />
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm">
                    <div>
                      <span
                        className={`font-semibold ${
                          isOverBudget
                            ? 'text-red-600 dark:text-red-400'
                            : isWarning
                            ? 'text-yellow-600 dark:text-yellow-400'
                            : 'text-green-600 dark:text-green-400'
                        }`}
                      >
                        {percentage.toFixed(1)}%
                      </span>
                      <span className="text-gray-500 dark:text-gray-400 ml-1">used</span>
                    </div>
                    <div className="text-right">
                      <span className="text-gray-500 dark:text-gray-400">
                        {remaining >= 0 ? 'Remaining: ' : 'Overspent: '}
                      </span>
                      <span
                        className={`font-semibold ${
                          remaining >= 0
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-red-600 dark:text-red-400'
                        }`}
                      >
                        {formatCurrency(Math.abs(remaining))}
                      </span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Create Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create Budget">
        <BudgetForm
          onSubmit={handleCreate}
          onCancel={() => setShowModal(false)}
          isLoading={createMutation.isPending}
          mode="create"
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingBudget}
        onClose={() => setEditingBudget(null)}
        title="Edit Budget"
      >
        {editingBudget && (
          <BudgetForm
            defaultValues={{
              category: editingBudget.category,
              budget_amount: editingBudget.budget_amount,
              month: editingBudget.month,
              year: editingBudget.year,
              alert_threshold_pct: editingBudget.alert_threshold_pct,
            }}
            onSubmit={handleUpdate}
            onCancel={() => setEditingBudget(null)}
            isLoading={updateMutation.isPending}
            mode="edit"
          />
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingBudget}
        onClose={() => setDeletingBudget(null)}
        onConfirm={handleDelete}
        title="Delete Budget"
        message={`Are you sure you want to delete the budget for ${deletingBudget?.category}? This action cannot be undone.`}
        confirmText="Delete"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />
    </div>
  )
}
