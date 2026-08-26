import { useState } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User, Mail, Lock, Trash2, Save } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card } from '@/components/common/Card'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { useAuth } from '@/contexts/AuthContext'
import { userService } from '@/services/user.service'
import { formatDate } from '@/utils'
import toast from 'react-hot-toast'

const profileSchema = z.object({
  full_name: z.string().min(1, 'Name is required').max(255),
  email: z.string().email('Invalid email'),
})

const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
})

type ProfileFormData = z.infer<typeof profileSchema>
type PasswordFormData = z.infer<typeof passwordSchema>

export function ProfilePage() {
  const { user, updateUser, logout } = useAuth()
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const profileForm = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
    },
  })

  const passwordForm = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  })

  const handleProfileUpdate = async (data: ProfileFormData) => {
    setIsUpdatingProfile(true)
    try {
      const updatedUser = await userService.updateProfile(data)
      updateUser(updatedUser)
      toast.success('Profile updated successfully')
    } catch {
      // Error handled by interceptor
    } finally {
      setIsUpdatingProfile(false)
    }
  }

  const handlePasswordChange = async (data: PasswordFormData) => {
    setIsChangingPassword(true)
    try {
      await userService.changePassword(data)
      toast.success('Password changed successfully')
      passwordForm.reset()
    } catch {
      // Error handled by interceptor
    } finally {
      setIsChangingPassword(false)
    }
  }

  const handleDeleteAccount = async () => {
    setIsDeleting(true)
    try {
      await userService.deleteAccount()
      toast.success('Account deleted')
      logout()
    } catch {
      // Error handled by interceptor
    } finally {
      setIsDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  if (!user) return null

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <PageHeader title="Profile" subtitle="Manage your account settings" />

      {/* Profile Info */}
      <Card>
        <div className="flex items-center gap-4 mb-6">
          <div className="h-16 w-16 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {user.full_name || 'User'}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              Member since {formatDate(user.created_at)}
            </p>
          </div>
        </div>
      </Card>

      {/* Edit Profile */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <User className="h-5 w-5" />
          Edit Profile
        </h3>
        <form onSubmit={profileForm.handleSubmit(handleProfileUpdate)} className="space-y-4">
          <Input
            label="Full Name"
            error={profileForm.formState.errors.full_name?.message}
            {...profileForm.register('full_name')}
          />
          <Input
            label="Email"
            type="email"
            error={profileForm.formState.errors.email?.message}
            {...profileForm.register('email')}
          />
          <Button type="submit" isLoading={isUpdatingProfile} leftIcon={<Save className="h-4 w-4" />}>
            Save Changes
          </Button>
        </form>
      </Card>

      {/* Change Password */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Lock className="h-5 w-5" />
          Change Password
        </h3>
        <form onSubmit={passwordForm.handleSubmit(handlePasswordChange)} className="space-y-4">
          <Input
            label="Current Password"
            type="password"
            error={passwordForm.formState.errors.current_password?.message}
            {...passwordForm.register('current_password')}
          />
          <Input
            label="New Password"
            type="password"
            placeholder="At least 8 characters"
            error={passwordForm.formState.errors.new_password?.message}
            {...passwordForm.register('new_password')}
          />
          <Button type="submit" isLoading={isChangingPassword}>
            Change Password
          </Button>
        </form>
      </Card>

      {/* Delete Account */}
      <Card className="border-red-200 dark:border-red-800">
        <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2 flex items-center gap-2">
          <Trash2 className="h-5 w-5" />
          Danger Zone
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <Button
          variant="danger"
          onClick={() => setShowDeleteConfirm(true)}
          leftIcon={<Trash2 className="h-4 w-4" />}
        >
          Delete Account
        </Button>
      </Card>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteAccount}
        title="Delete Account"
        message="Are you sure you want to delete your account? All your data will be permanently removed."
        confirmText="Delete Account"
        isLoading={isDeleting}
        variant="danger"
      />
    </div>
  )
}
