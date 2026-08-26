import os

# Inspect Sidebar.tsx around line 196
path = 'frontend/src/components/layout/Sidebar.tsx'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Sidebar.tsx total lines: {len(lines)}')
print('===== Last 30 lines =====')
for i in range(max(0, len(lines)-30), len(lines)):
    print(f'{i+1}: {repr(lines[i])}')

print()
print('===== DashboardPage.tsx around lines 120-130 =====')
path2 = 'frontend/src/pages/dashboard/DashboardPage.tsx'
with open(path2, 'r', encoding='utf-8') as f:
    lines2 = f.readlines()
print(f'DashboardPage.tsx total lines: {len(lines2)}')
for i in range(119, min(130, len(lines2))):
    print(f'{i+1}: {repr(lines2[i])}')

print()
print('===== DashboardPage.tsx around lines 200-230 =====')
for i in range(199, min(230, len(lines2))):
    print(f'{i+1}: {repr(lines2[i])}')

print()
print('===== DashboardPage.tsx last 30 lines =====')
for i in range(max(0, len(lines2)-30), len(lines2)):
    print(f'{i+1}: {repr(lines2[i])}')
