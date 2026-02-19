# Quick Start: Deploy to HostAfrica

## 🚀 Fast Track (If You're Experienced)

### 1. Prepare Locally
```bash
# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update settings.py with:
# - SECRET_KEY
# - ALLOWED_HOSTS = ['yourdomain.com']
# - DEBUG = False
# - Production M-Pesa credentials
```

### 2. Upload to HostAfrica
```bash
# Via SSH:
cd ~/public_html
git clone https://github.com/yourusername/your-repo.git .
```

### 3. Setup on Server
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with production values
nano .env

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Configure
- Create database in cPanel
- Install SSL certificate
- Update database settings in settings.py

### 5. Test
- Visit https://yourdomain.com
- Test payment flow

---

## 📖 For Detailed Steps

See **STEP_BY_STEP_DEPLOYMENT.md** for complete beginner-friendly guide.

---

## ⚡ Common Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin user
python manage.py createsuperuser

# Check for errors
python manage.py check --deploy

# View logs
tail -f ~/logs/error_log
```

---

## 🔑 Important Files

- `.env` - Environment variables (SECRET_KEY, database, M-Pesa credentials)
- `passenger_wsgi.py` - WSGI configuration
- `.htaccess` - Apache configuration
- `config/settings.py` - Django settings

---

## 📝 Environment Variables Template

Create `.env` file with:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
MPESA_ENV=production
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_BASE_URL=https://yourdomain.com
```
