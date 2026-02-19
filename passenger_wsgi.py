"""
Passenger WSGI file for HostAfrica deployment.
This file should be in your project root (same level as manage.py).
"""
import sys
import os

# Add your project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
