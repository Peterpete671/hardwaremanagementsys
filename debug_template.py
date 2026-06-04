from pathlib import Path

path = Path('frontend/templates/frontend/base.html')
for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
    print(f'{i}: {line}')
