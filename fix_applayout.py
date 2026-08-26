path = 'frontend/src/components/layout/AppLayout.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The file currently ends with:
#         <Footer />
#       </div>
#   )
# Missing closing </div> for the outer div.

old = """        <Footer />
      </div>
  )
}"""

new = """        <Footer />
      </div>
  )
}"""

if old in content:
    content = content.replace(old, new)
    print('Found and replaced pattern')
else:
    print('Pattern not found, checking current content:')
    print(repr(content[-200:]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Open divs:', content.count('<div'))
print('Close divs:', content.count('</div>'))
