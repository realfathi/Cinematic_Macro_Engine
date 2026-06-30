import re

with open('e:/Cinematic_Macro_Engine/src/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix literal backslashes in f-strings
content = content.replace('f\\\"\\\"\\\"', 'f\"\"\"')

# Fix double injections
pattern = r'WHERE f\.revenue > 0 \{get_era_filter_clause\(era_filter\)\} AND f\.budget > 0 \{get_era_filter_clause\(era_filter\)\}'
replacement = r'WHERE f.revenue > 0 AND f.budget > 0 {get_era_filter_clause(era_filter)}'
content = re.sub(pattern, replacement, content)

with open('e:/Cinematic_Macro_Engine/src/database.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Cleanup completed.')
