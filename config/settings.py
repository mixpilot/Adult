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
SECRET_KEY = 'django-insecure-change-this-in-production-!@#$%^&*()'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


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
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
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
MPESA_ENV = os.environ.get('MPESA_ENV', 'sandbox')  # sandbox | production
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '')  # Till or Paybill
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', '')
# Base URL for callbacks (must be HTTPS in production). Daraja will POST to {MPESA_CALLBACK_BASE_URL}/payments/mpesa/callback/
MPESA_CALLBACK_BASE_URL = os.environ.get('MPESA_CALLBACK_BASE_URL', 'https://yourdomain.com')

# Paystack (same endpoints for test/live; keys selected by env)
PAYSTACK_ENV = os.environ.get('PAYSTACK_ENV', 'sandbox').lower()  # sandbox | live
PAYSTACK_BASE_URL = os.environ.get('PAYSTACK_BASE_URL', 'https://api.paystack.co')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY', '')
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY', '')
PAYSTACK_TEST_PUBLIC_KEY = os.environ.get('PAYSTACK_TEST_PUBLIC_KEY', '')
PAYSTACK_TEST_SECRET_KEY = os.environ.get('PAYSTACK_TEST_SECRET_KEY', '')
PAYSTACK_LIVE_PUBLIC_KEY = os.environ.get('PAYSTACK_LIVE_PUBLIC_KEY', '')
PAYSTACK_LIVE_SECRET_KEY = os.environ.get('PAYSTACK_LIVE_SECRET_KEY', '')
PAYSTACK_CALLBACK_BASE_URL = os.environ.get('PAYSTACK_CALLBACK_BASE_URL', '')

if PAYSTACK_ENV == 'live':
    PAYSTACK_PUBLIC_KEY_ACTIVE = PAYSTACK_LIVE_PUBLIC_KEY or PAYSTACK_PUBLIC_KEY
    PAYSTACK_SECRET_KEY_ACTIVE = PAYSTACK_LIVE_SECRET_KEY or PAYSTACK_SECRET_KEY
else:
    PAYSTACK_PUBLIC_KEY_ACTIVE = PAYSTACK_TEST_PUBLIC_KEY or PAYSTACK_PUBLIC_KEY
    PAYSTACK_SECRET_KEY_ACTIVE = PAYSTACK_TEST_SECRET_KEY or PAYSTACK_SECRET_KEY

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
