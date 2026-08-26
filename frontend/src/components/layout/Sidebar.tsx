import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  BarChart3,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
  X,
  LogOut,
  Wallet,
  Heart,
  LineChart,
  Home,
  MessageSquare,
  FileText,
  Globe,
  PieChart as PieChartIcon,
  Car,
  Sparkles,
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { classNames } from '@/utils'

const navItems = [
  { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Incomes', path: '/incomes', icon: TrendingUp },
  { label: 'Expenses', path: '/expenses', icon: TrendingDown },
  { label: 'Budgets', path: '/budgets', icon: PiggyBank },
  { label: 'Monthly Summary', path: '/monthly-summary', icon: BarChart3 },
  { label: 'Financial Health', path: '/financial-health', icon: Heart },
  { label: 'Investment Advisor', path: '/investment-advisor', icon: TrendingUp },
  { label: 'Stock Prediction', path: '/stock-prediction', icon: LineChart },
  { label: 'Market Analysis', path: '/market-analysis', icon: Globe },
  { label: 'Mutual Funds', path: '/mutual-funds', icon: PieChartIcon },
  { label: 'Wealth Projection', path: '/wealth-projection', icon: Car },
  { label: 'House Price', path: '/house-price', icon: Home },
  { label: 'AI Assistant', path: '/ai-chat', icon: MessageSquare },
  { label: 'Reports', path: '/reports', icon: FileText },
  { label: 'Analytics', path: '/analytics', icon: BarChart3 },
  { label: 'Profile', path: '/profile', icon: User },
  { label: 'Settings', path: '/settings', icon: Settings },
]

interface SidebarProps {
  isMobileOpen: boolean
  onMobileClose: () => void
  collapsed: boolean
  onCollapse: (collapsed: boolean) => void
}

export function Sidebar({ isMobileOpen, onMobileClose, collapsed, onCollapse }: SidebarProps) {
  const location = useLocation()
  const { user, logout } = useAuth()

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-gray-200 dark:border-gray-700">
        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
          <Wallet className="h-6 w-6 text-primary-600 dark:text-primary-400" />
        </div>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="flex-1"
          >
            <h1 className="text-sm font-bold text-gray-900 dark:text-gray-100 leading-tight">
              Finance
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">Advisor</p>
          </motion.div>
        )}
        {!collapsed && (
          <button
            onClick={() => onCollapse(true)}
            className="hidden lg:flex p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        )}
        {collapsed && (
          <button
            onClick={() => onCollapse(false)}
            className="hidden lg:flex p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        )}
      </div>
      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onMobileClose}
              className={classNames(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group',
                isActive
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200'
              )}
            >
              <item.icon className={classNames('h-5 w-5 flex-shrink-0', isActive ? 'text-primary-600 dark:text-primary-400' : '')} />
              {!collapsed && (
                <span className="text-sm whitespace-nowrap">{item.label}</span>
              )}
              {isActive && !collapsed && (
                <motion.div
                  layoutId="activeNav"
                  className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-600 dark:bg-primary-400"
                />
              )}
            </Link>
          )
        })}
      </nav>
      {/* User section */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        {!collapsed && user && (
          <div className="flex items-center gap-3 mb-3 px-2">
            <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <span className="text-sm font-semibold text-primary-600 dark:text-primary-400">
                {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {user.full_name || 'User'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user.email}
              </p>
            </div>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={classNames(
          'hidden lg:flex flex-col fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-30 transition-all duration-300',
          collapsed ? 'w-20' : 'w-64'
        )}
      >
        {sidebarContent}
      </aside>
      {/* Mobile Sidebar */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
              onClick={onMobileClose}
            />
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed left-0 top-0 h-full w-72 bg-white dark:bg-gray-800 z-50 lg:hidden shadow-2xl"
            >
              <div className="flex justify-end p-4">
                <button
                  onClick={onMobileClose}
                  className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
