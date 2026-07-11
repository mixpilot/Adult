"""
Passenger WSGI entrypoint for HostAfrica / cPanel.
Logs startup failures to startup_error.log in the project root.
"""
import os
import sys
import traceback

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Load .env before Django (Passenger cwd may differ from manage.py)
_env_file = os.path.join(_PROJECT_DIR, '.env')
if os.path.isfile(_env_file):
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception:
    _log = os.path.join(_PROJECT_DIR, 'startup_error.log')
    with open(_log, 'a', encoding='utf-8') as fh:
        fh.write('\n--- Passenger startup error ---\n')
        fh.write(traceback.format_exc())
    raise
