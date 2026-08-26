import os

files_to_check = [
    'frontend/src/components/layout/Sidebar.tsx',
    'frontend/src/pages/dashboard/DashboardPage.tsx',
    'frontend/src/components/layout/AppLayout.tsx',
]

for path in files_to_check:
    print(f'===== {path} =====')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f'Size: {len(content)} bytes')
        # Check for corruption markers
        for marker in ['</parameter>', '</invoke>', '</tool_calls>', 'parameter_name', 'invoke name']:
            if marker in content:
                idx = content.find(marker)
                print(f'  CORRUPTION MARKER "{marker}" found at index {idx}')
                print(f'  Context: ...{content[max(0,idx-50):idx+80]}...')
        print()
    else:
        print('  FILE NOT FOUND')
        print()
