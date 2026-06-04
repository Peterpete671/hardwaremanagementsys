import os
import glob
from pathlib import Path
import django
import subprocess

root = Path(__file__).resolve().parent
os.chdir(root)

with open(root / 'check_results.txt', 'w', encoding='utf-8') as f:
    f.write('TEMPLATE COMPILE:\n')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardwaremngmtsys.settings')
    try:
        django.setup()
        from django.template import engines
        from django.template.exceptions import TemplateSyntaxError
        all_ok = True
        for path in glob.glob(str(root / 'frontend' / 'templates' / 'frontend' / '*.html')):
            src = Path(path).read_text(encoding='utf-8')
            try:
                engines['django'].from_string(src)
            except TemplateSyntaxError as e:
                all_ok = False
                f.write(f'{path} -> {e}\n')
        if all_ok:
            f.write('ALL TEMPLATES COMPILED OK\n')
    except Exception as e:
        f.write('ERROR DURING TEMPLATE SETUP: ' + repr(e) + '\n')
    f.write('\nDJANGO CHECK:\n')
    try:
        p = subprocess.run(['py','-3','manage.py','check'], capture_output=True, text=True)
        f.write('returncode=' + str(p.returncode) + '\n')
        f.write('stdout:\n' + p.stdout + '\n')
        f.write('stderr:\n' + p.stderr + '\n')
    except Exception as e:
        f.write('CHECK FAILED: ' + repr(e) + '\n')
    f.write('\nDJANGO TEST:\n')
    try:
        p = subprocess.run(['py','-3','manage.py','test'], capture_output=True, text=True)
        f.write('returncode=' + str(p.returncode) + '\n')
        f.write('stdout:\n' + p.stdout + '\n')
        f.write('stderr:\n' + p.stderr + '\n')
    except Exception as e:
        f.write('TEST FAILED: ' + repr(e) + '\n')
