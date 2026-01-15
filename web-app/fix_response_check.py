with open('website_auditor.py', 'r') as f:
    content = f.read()

# Replace the broken check
old = '''        print(f"DEBUG: response is {response}, type: {type(response)}")
        if not response:
            print(f"🚨 DEBUG: INSIDE if not response block! response={response}")'''

new = '''        print(f"DEBUG: response is {response}, type: {type(response)}")
        if response is None:
            print(f"🚨 DEBUG: Response is None!")'''

content = content.replace(old, new)

with open('website_auditor.py', 'w') as f:
    f.write(content)
print("✅ Fixed the bug!")
