# HostAfrica Deployment Guide

This guide will help you deploy your Django application to HostAfrica.

## Prerequisites

1. HostAfrica hosting account with Python support
2. Domain name pointed to HostAfrica
3. Database (PostgreSQL or MySQL) - check with HostAfrica support
4. SSH access (if available) or cPanel File Manager

## Step 1: Prepare Your Project

### 1.1 Update Settings for Production

Before deploying, update `config/settings.py`:

```python
# Change these settings:
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'your-production-secret-key-here'  # Generate a new one!

# Update M-Pesa callback URL:
MPESA_CALLBACK_BASE_URL = 'https://yourdomain.com'
MPESA_ENV = 'production'  # Change from 'sandbox' to 'production'
```

### 1.2 Generate New Secret Key

Run this locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` in production.

## Step 2: Upload Files to HostAfrica

### Option A: Using Git (Recommended)

1. Push your code to GitHub/GitLab
2. SSH into HostAfrica server
3. Clone the repository:
```bash
cd ~/public_html  # or your domain directory
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### Option B: Using cPanel File Manager

1. Log into cPanel
2. Go to File Manager
3. Navigate to `public_html` (or your domain directory)
4. Upload all project files (zip and extract, or use FTP)

## Step 3: Set Up Virtual Environment

SSH into your HostAfrica server:

```bash
cd ~/public_html/your-project
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Database

### If using PostgreSQL:

1. Create database in cPanel → PostgreSQL Databases
2. Update `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### If using MySQL:

1. Create database in cPanel → MySQL Databases
2. Update `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Step 5: Environment Variables

Create a `.env` file in your project root (or set in cPanel):

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname
MPESA_CONSUMER_KEY=your-production-consumer-key
MPESA_CONSUMER_SECRET=your-production-consumer-secret
MPESA_SHORTCODE=your-production-shortcode
MPESA_PASSKEY=your-production-passkey
MPESA_ENV=production
MPESA_CALLBACK_BASE_URL=https://yourdomain.com
```

## Step 6: Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Step 7: Configure WSGI

HostAfrica typically uses Passenger or mod_wsgi. Create `passenger_wsgi.py` in your project root:

```python
import sys
import os

# Add your project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 8: Static Files Configuration

Create `.htaccess` in your `public_html`:

```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    
    # Serve static files
    RewriteRule ^static/(.*)$ staticfiles/$1 [L]
    
    # Serve media files
    RewriteRule ^media/(.*)$ media/$1 [L]
    
    # Pass all other requests to Django
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ passenger_wsgi.py/$1 [L]
</IfModule>
```

## Step 9: SSL Certificate

1. In cPanel, go to SSL/TLS
2. Install Let's Encrypt SSL (free)
3. Force HTTPS redirect in Django settings:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Step 10: Update M-Pesa Production Credentials

1. Log into Daraja portal: https://developer.safaricom.co.ke/
2. Get your production Consumer Key and Secret
3. Update in `.env` or cPanel environment variables
4. Update `MPESA_CALLBACK_BASE_URL` to your domain

## Step 11: Test Deployment

1. Visit your domain
2. Test user registration
3. Test subscription payment flow
4. Check M-Pesa callback is working

## Troubleshooting

### Static files not loading:
```bash
python manage.py collectstatic --noinput
```

### Permission issues:
```bash
chmod 755 manage.py
chmod -R 755 staticfiles
chmod -R 755 media
```

### Database connection errors:
- Check database credentials in cPanel
- Verify database user has proper permissions
- Check if database host is correct (might be different from localhost)

### M-Pesa callbacks not working:
- Verify SSL is installed and working
- Check `MPESA_CALLBACK_BASE_URL` is correct
- Test callback URL is accessible: `https://yourdomain.com/payments/mpesa/callback/`

## Support

- HostAfrica Support: Check their documentation or contact support
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
