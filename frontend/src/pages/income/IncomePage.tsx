import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, Pencil, Trash2, TrendingUp } from 'lucide-react'
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
import { IncomeForm } from '@/components/forms/IncomeForm'
import { useIncomes, useCreateIncome, useUpdateIncome, useDeleteIncome } from '@/hooks/useIncomes'
import { useDebounce } from '@/hooks/useDebounce'
import { formatCurrency, formatDate } from '@/utils'
import { IncomeCreate, IncomeUpdate, IncomeRead } from '@/types'

export function IncomePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 500)
  const [showModal, setShowModal] = useState(searchParams.get('add') === 'true')
  const [editingIncome, setEditingIncome] = useState<IncomeRead | null>(null)
  const [deletingIncome, setDeletingIncome] = useState<IncomeRead | null>(null)

  const { data, isLoading, error, refetch } = useIncomes({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
  })

  const createMutation = useCreateIncome()
  const updateMutation = useUpdateIncome()
  const deleteMutation = useDeleteIncome()

  const handleCreate = async (formData: IncomeCreate | IncomeUpdate) => {
    await createMutation.mutateAsync(formData as IncomeCreate)
    setShowModal(false)
  }

  const handleUpdate = async (formData: IncomeCreate | IncomeUpdate) => {
    if (!editingIncome) return
    await updateMutation.mutateAsync({ id: editingIncome.id, data: formData as IncomeUpdate })
    setEditingIncome(null)
  }

  const handleDelete = async () => {
    if (!deletingIncome) return
    await deleteMutation.mutateAsync(deletingIncome.id)
    setDeletingIncome(null)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Incomes"
        subtitle="Manage your income sources"
        action={
          <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
            Add Income
          </Button>
        }
      />

      <Card padding="sm">
        <div className="flex flex-col sm:flex-row gap-4 p-4">
          <SearchBox value={search} onChange={setSearch} placeholder="Search incomes..." className="flex-1" />
        </div>

        {error ? (
          <ErrorMessage onRetry={refetch} />
        ) : isLoading ? (
          <div className="p-4">
            <TableSkeleton rows={5} />
          </div>
        ) : !data?.items?.length ? (
          <EmptyState
            icon={<TrendingUp className="h-12 w-12" />}
            title="No incomes found"
            description="Add your first income to start tracking your earnings"
            action={
              <Button onClick={() => setShowModal(true)} leftIcon={<Plus className="h-4 w-4" />}>
                Add Income
              </Button>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Source</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Frequency</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {data.items.map((income, index) => (
                  <motion.tr
                    key={income.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{income.source}</span>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="info">{income.category}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                        {formatCurrency(income.amount)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">{income.frequency}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">{formatDate(income.received_date)}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingIncome(income)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeletingIncome(income)}
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
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add Income">
        <IncomeForm
          onSubmit={handleCreate}
          onCancel={() => setShowModal(false)}
          isLoading={createMutation.isPending}
          mode="create"
        />
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingIncome}
        onClose={() => setEditingIncome(null)}
        title="Edit Income"
      >
        {editingIncome && (
          <IncomeForm
            defaultValues={{
              source: editingIncome.source,
              category: editingIncome.category,
              amount: editingIncome.amount,
              frequency: editingIncome.frequency,
              received_date: editingIncome.received_date,
              description: editingIncome.description || '',
            }}
            onSubmit={handleUpdate}
            onCancel={() => setEditingIncome(null)}
            isLoading={updateMutation.isPending}
            mode="edit"
          />
        )}
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={!!deletingIncome}
        onClose={() => setDeletingIncome(null)}
        onConfirm={handleDelete}
        title="Delete Income"
        message={`Are you sure you want to delete the income "${deletingIncome?.source}"? This action cannot be undone.`}
        confirmText="Delete"
        isLoading={deleteMutation.isPending}
        variant="danger"
      />
    </div>
  )
}
