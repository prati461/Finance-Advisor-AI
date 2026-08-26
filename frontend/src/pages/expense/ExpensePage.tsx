import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, Pencil, Trash2, TrendingDown } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { SearchBox } from '@/components/common/SearchBox'
import { Pagination } from '@/components/common/Pagination'
import { Modal } from '@/components/common/Modal'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Badge } from '@/components/common/Badge'
import { EmptyState } from '@/components/common/EmptyState'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import { TableSkeleton } from '@/components/common/Skeleton'
import { ExpenseForm } from '@/components/forms/ExpenseForm'
import { useExpenses, useCreateExpense, useUpdateExpense, useDeleteExpense } from '@/hooks/useExpenses'
import { useDebounce } from '@/hooks/useDebounce'
import { formatCurrency, formatDate } from '@/utils'
import { ExpenseCreate, ExpenseUpdate, ExpenseRead } from '@/types'

export function ExpensePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 500)
  const [showModal, setShowModal] = useState(searchParams.get('add') === 'true')
  const [editingExpense, setEditingExpense] = useState<ExpenseRead | null>(null)
  const [deletingExpense, setDeletingExpense] = useState<ExpenseRead | null>(null)

  const { data, isLoading, error, refetch } = useExpenses({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
  })

  const createMutation = useCreateExpense()
  const updateMutation = useUpdateExpense()
  const deleteMutation = useDeleteExpense()

  const handleCreate = async (formData: ExpenseCreate | ExpenseUpdate) => {
    await createMutation.mutateAsync(formData as ExpenseCreate)
    setShowModal(false)
  }

  const handleUpdate = async (formData: ExpenseCreate | ExpenseUpdate) => {
    if (!editingExpense) return
    await updateMutation.mutateAsync({ id: editingExpense.id, data: formData as ExpenseUpdate })
    setEditingExpense(null)
  }

  const handleDelete = async () => {
    if (!deletingExpense) return
    await deleteMutation.mutateAsync(deletingExpense.id)
    setDeletingExpense(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Expenses"
        subtitle="Track your expenses"
        action={
          <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
            Add Expense
          </Button>
        }
      />

      <Card padding="sm">
        <div className="flex flex-col sm:flex-row gap-4 p-4">
          <SearchBox value={search} onChange={setSearch} placeholder="Search expenses..." className="flex-1" />
        </div>

        {error ? (
          <ErrorMessage onRetry={refetch} />
        ) : isLoading ? (
          <div className="p-4">
            <TableSkeleton rows={5} />
          </div>
        ) : !data?.items?.length ? (
          <EmptyState
            icon={<TrendingDown className="h-12 w-12" />}
            title="No expenses found"
            description="Add your first expense to start tracking"
            action={
              <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
                Add Expense
              </Button>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Merchant</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Payment</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {data.items.map((expense, index) => (
                  <motion.tr
                    key={expense.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <Badge variant="warning">{expense.category}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-semibold text-red-600 dark:text-red-400">
                        {formatCurrency(expense.amount)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {expense.merchant || '-'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">{formatDate(expense.spent_at)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {expense.payment_method || '-'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingExpense(expense)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeletingExpense(expense)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {data && data.total > 0 && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <Pagination
              page={data.page}
              pageSize={data.page_size}
              total={data.total}
              onPageChange={setPage}
            />
          </div>
        )}
      </Card>

      {/* Create Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add Expense">
        <ExpenseForm
          onSubmit={handleCreate}
          onCancel={() => setShowModal(false)}
          isLoading={createMutation.isPending}
          mode="create"
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingExpense}
        onClose={() => setEditingExpense(null)}
        title="Edit Expense"
      >
        {editingExpense && (
          <ExpenseForm
            defaultValues={{
              category: editingExpense.category,
              amount: editingExpense.amount,
              spent_at: editingExpense.spent_at,
              description: editingExpense.description || '',
              merchant: editingExpense.merchant || '',
              payment_method: editingExpense.payment_method || '',
            }}
            onSubmit={handleUpdate}
            onCancel={() => setEditingExpense(null)}
            isLoading={updateMutation.isPending}
            mode="edit"
          />
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingExpense}
        onClose={() => setDeletingExpense(null)}
        onConfirm={handleDelete}
        title="Delete Expense"
        message={`Are you sure you want to delete this expense of ${deletingExpense ? formatCurrency(deletingExpense.amount) : ''}? This action cannot be undone.`}
        confirmText="Delete"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />
    </div>
  )
}
