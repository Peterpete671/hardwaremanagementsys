import os, django
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE','hardwaremngmtsys.settings')
django.setup()
from django.template import engines
template_dir = Path('frontend/templates/frontend')
templates = list(template_dir.glob('*.html'))
errors = []
for t in templates:
    try:
        src = t.read_text(encoding='utf-8')
        engines['django'].from_string(src)
    except Exception as e:
        errors.append(f'{t.name}: {e}')
if errors:
    for e in errors:
        print(e)
else:
    print('all templates OK')
