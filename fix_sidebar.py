with open('frontend/src/components/layout/Sidebar.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# The issue: the sidebarContent JSX is missing the closing </div> for the root div
# After:       </div> (closing p-4 border-t... div)
# We need:    </div> (closing flex flex-col h-full div)
# Then:       )

# Find the pattern around the end of sidebarContent
old = """        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
  )"""

new = """        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
  )"""

content = content.replace(old, new)

with open('frontend/src/components/layout/Sidebar.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
open_divs = content.count('<div')
close_divs = content.count('</div>')
print(f"Open divs: {open_divs}, Close divs: {close_divs}")
if open_divs == close_divs:
    print("All divs properly closed!")
else:

