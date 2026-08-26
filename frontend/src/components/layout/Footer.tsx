export function Footer() {
  return (
    <footer className="py-4 px-6 border-t border-gray-200 dark:border-gray-700">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-gray-500 dark:text-gray-400">
        <p>&copy; {new Date().getFullYear()} Finance Advisor. All rights reserved.</p>
        <p>Built with React, TypeScript & Tailwind CSS</p>
      </div>
    </footer>
  )
}
