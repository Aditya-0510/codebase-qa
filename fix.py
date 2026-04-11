import os

for root, _, files in os.walk(r'd:\Projects\codebase-qa'):
    for f in files:
        if f.endswith(('.py', '.js')) and f != 'fix.py':
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if r'\"' in content:
                new_content = content.replace(r'\"', '\"')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Fixed {path}")
