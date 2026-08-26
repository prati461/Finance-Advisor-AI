import sys

path = 'frontend/src/components/layout/Sidebar.tsx'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to add a closing </div> after the "      </div>" that closes the
# "p-4 border-t" div and before the "  )" that closes sidebarContent.
# Target: 
#         </button>
#       </div>
#   )
# Should become:
#         </button>
#       </div>
#     </div>
#   )

out = []
i = 0
while i < len(lines):
    out.append(lines[i])
    if lines[i].rstrip() == '      </div>':
        # check next non-empty line is '  )'
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        if j < len(lines) and lines[j].rstrip() == '  )':
            # Insert closing div for root container
            out.append('    </div>\n')
    i += 1

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
open_divs = content.count('<div')
close_divs = content.count('</div>')
print('Open divs:', open_divs, 'Close divs:', close_divs)
print('Balanced' if open_divs == close_divs else 'NOT BALANCED')
