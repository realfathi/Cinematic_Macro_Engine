with open('e:/Cinematic_Macro_Engine/src/database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'runtime' in line.lower():
        print(f'{i+1}: {line.strip()}')
