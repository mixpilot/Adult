"""
Django settings for adult entertainment website project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env (project root)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-!@#$%^&*()')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Allowed hosts - update for production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'content',
    'core',
    'connections',
    'subscriptions',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.connection_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Use PostgreSQL/MySQL in production, SQLite for development
if os.environ.get('DATABASE_NAME'):
    # Production database (PostgreSQL or MySQL)
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DATABASE_NAME', ''),
            'USER': os.environ.get('DATABASE_USER', ''),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
            'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
            'PORT': os.environ.get('DATABASE_PORT', '5432'),
        }
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Session Configuration
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (default for "Remember Me")
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Allow set_expiry() to control expiry
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = False  # Don't save session on every request

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB

# Cache configuration (for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email configuration (for password reset)
# For development, emails are printed to console
# For production, configure SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@adultentertainment.com'

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_publishable_key_here')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_secret_key_here')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here')

# Currency Settings
CURRENCY_CODE = 'KES'
CURRENCY_SYMBOL = 'KSh'
USD_TO_KES_RATE = 130  # Approximate conversion rate (adjust as needed)

# Subscription Settings
SUBSCRIPTION_TRIAL_DAYS = 7  # 7-day free trial
TOKEN_PRICE = 13.00  # KSh 13.00 per token (approximately $0.10)
CREATOR_REVENUE_SHARE = 70  # 70% to creator, 30% to platform

# M-Pesa (Daraja API) – STK Push / prompt only
# Accept: sandbox | production | live | prod (live/prod → production API)
_raw_mpesa_env = os.environ.get('MPESA_ENV', 'sandbox').strip().lower()
MPESA_ENV = 'sandbox' if _raw_mpesa_env == 'sandbox' else 'production'
# Daraja API Credentials (remove spaces when copying from portal)
# Consumer Key from image: TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTz F7Bzab3uuiUwH (space removed)
# Consumer Secret from image: ws93rCpBMO9EyUJr16LmGAyXA4bEYOGA3I WiPWaqosf66NsgRzBGgIN7weR6q4hQ (space removed)
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTzF7Bzab3uuiUwH').strip().replace(' ', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'ws93rCpBMO9EyUJr16LmGAyXA4bEY0GA3lWiPWaqosf66NsgRzBGglN7weR6q4hQ').strip().replace(' ', '')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')  # Test shortcode for sandbox
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Test passkey for sandbox
# till = Buy Goods (CustomerBuyGoodsOnline) | paybill = Pay Bill (CustomerPayBillOnline)
MPESA_SHORTCODE_TYPE = os.environ.get('MPESA_SHORTCODE_TYPE', 'till').strip().lower()
# Till STK: BusinessShortCode = head office / agent number (passkey is for this number).
# PartyB = till / store number — set MPESA_TILL_NUMBER (or MPESA_PARTY_B).
MPESA_TILL_NUMBER = os.environ.get('MPESA_TILL_NUMBER', '').strip() or None
MPESA_PARTY_B = os.environ.get('MPESA_PARTY_B', '').strip() or MPESA_TILL_NUMBER or None
# Base URL for callbacks (must be HTTPS in production). Daraja will POST to {MPESA_CALLBACK_BASE_URL}/payments/mpesa/callback/
# For local testing, use ngrok: https://your-ngrok-url.ngrok.io
# For sandbox testing, you can use a placeholder - the system will use status polling as fallback
MPESA_CALLBACK_BASE_URL = os.environ.get('MPESA_CALLBACK_BASE_URL', 'https://sandbox.safaricom.co.ke')

# Daraja API Settings (alternative naming for compatibility)
DARAJACONSUMER_KEY = MPESA_CONSUMER_KEY
DARAJACONSUMER_SECRET = MPESA_CONSUMER_SECRET
DARAJASHORTCODE = MPESA_SHORTCODE
DARAJAPASSKEY = MPESA_PASSKEY
DARAJASANDBOX = (MPESA_ENV == 'sandbox')

# Django Unfold Configuration – light theme, red/valentine colours
UNFOLD = {
    "SITE_TITLE": "Mali Safi Escorts Admin",
    "SITE_HEADER": "Mali Safi Escorts",
    "SITE_URL": "/",
    "SITE_SYMBOL": "favorite",  # heart-style icon
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "THEME": "light",
    "COLORS": {
        "primary": {
            "50": "oklch(0.98 0.02 15)",
            "100": "oklch(0.94 0.05 18)",
            "200": "oklch(0.88 0.10 18)",
            "300": "oklch(0.80 0.16 18)",
            "400": "oklch(0.68 0.22 18)",
            "500": "oklch(0.58 0.24 18)",
            "600": "oklch(0.50 0.22 18)",
            "700": "oklch(0.42 0.20 18)",
            "800": "oklch(0.34 0.16 18)",
            "900": "oklch(0.26 0.12 18)",
            "950": "oklch(0.18 0.08 18)",
        },
    },
}

# ============================================
# HTTPS & SECURITY SETTINGS (Production)
# ============================================
# Only enable in production (when DEBUG=False)
if not DEBUG:
    # Force HTTPS redirects
    SECURE_SSL_REDIRECT = True
    
    # Secure cookies (only sent over HTTPS)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Prevent clickjacking and XSS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security) - tells browsers to always use HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
