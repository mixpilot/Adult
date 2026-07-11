#!/usr/bin/env python
"""
Production startup diagnostic. Run on server:
  source .../bin/activate && cd .../Adult && python diagnose_startup.py
"""
import os
import sys
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

print('Project:', BASE)
print('billing.py:', os.path.isfile(os.path.join(BASE, 'subscriptions', 'billing.py')))
print('.env:', os.path.isfile(os.path.join(BASE, '.env')))

if os.path.isfile(os.path.join(BASE, '.env')):
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(BASE, '.env'))
        print('DATABASE_NAME set:', bool(os.environ.get('DATABASE_NAME')))
        print('DEBUG:', os.environ.get('DEBUG', '(not set)'))
    except ImportError as e:
        print('dotenv import failed:', e)

try:
    import django
    django.setup()
    print('django.setup: OK')
except Exception:
    print('django.setup FAILED:')
    traceback.print_exc()
    sys.exit(1)

try:
    from django.core.wsgi import get_wsgi_application
    get_wsgi_application()
    print('WSGI: OK')
except Exception:
    print('WSGI FAILED:')
    traceback.print_exc()
    sys.exit(1)

try:
    from django.core.management import call_command
    call_command('check')
    print('manage.py check: OK')
except Exception:
    print('check FAILED:')
    traceback.print_exc()
    sys.exit(1)

print('\nAll checks passed. If the site still fails, restart the Python app in cPanel.')
