# Step-by-Step Guide: Deploy to HostAfrica

This is a complete beginner-friendly guide to deploy your Django application to HostAfrica.

---

## 📋 PHASE 1: PREPARATION (Do This First)

### Step 1.1: Get Your HostAfrica Account Ready

1. **Sign up for HostAfrica hosting**
   - Go to https://www.hostafrica.co.za/
   - Choose a hosting plan (Python/Django support required)
   - Complete registration and payment

2. **Get your hosting details**
   - Note down your:
     - cPanel username and password
     - FTP credentials (if provided)
     - SSH access details (if available)
     - Nameservers (for domain pointing)

### Step 1.2: Get Your Domain

1. **Purchase domain** (if you don't have one)
   - From HostAfrica or any registrar (Namecheap, GoDaddy, etc.)
   - Example: `yourdomain.com`

2. **Point domain to HostAfrica**
   - Update nameservers at your domain registrar
   - Use the nameservers provided by HostAfrica
   - Wait 24-48 hours for DNS propagation

### Step 1.3: Get Production M-Pesa Credentials

1. **Log into Daraja Portal**
   - Go to https://developer.safaricom.co.ke/
   - Log in with your account

2. **Get Production Credentials**
   - Navigate to your app (or create production app)
   - Copy:
     - Consumer Key
     - Consumer Secret
     - Shortcode (Paybill/Till number)
     - Passkey

3. **Note them down** - You'll need them later

---

## 📦 PHASE 2: PREPARE YOUR PROJECT (On Your Computer)

### Step 2.1: Generate Production Secret Key

Open terminal/command prompt in your project folder:

```bash
cd C:\Users\ADMIN\PycharmProjects\Adult
python manage.py shell
```

Then in Python shell:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

**Copy the output** - This is your production SECRET_KEY

### Step 2.2: Update Settings for Production

1. **Open** `config/settings.py`

2. **Find and update these lines** (around line 22-27):

```python
# Change from:
SECRET_KEY = 'django-insecure-change-this-in-production-!@#$%^&*()'
DEBUG = True
ALLOWED_HOSTS = ['*']

# To (use your actual domain):
SECRET_KEY = os.environ.get('SECRET_KEY', 'paste-your-generated-secret-key-here')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'yourdomain.com,www.yourdomain.com').split(',')
```

3. **Update M-Pesa settings** (around line 193-200):

```python
# Change from sandbox to production:
MPESA_ENV = os.environ.get('MPESA_ENV', 'production')  # Changed from 'sandbox'
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'your-production-consumer-key')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'your-production-consumer-secret')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', 'your-production-shortcode')
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'your-production-passkey')
MPESA_CALLBACK_BASE_URL = os.environ.get('MPESA_CALLBACK_BASE_URL', 'https://yourdomain.com')
```

**Replace `yourdomain.com` with your actual domain!**

### Step 2.3: Test Locally (Optional but Recommended)

```bash
python manage.py check --deploy
python manage.py collectstatic --noinput
```

If no errors, you're good to go!

### Step 2.4: Commit Changes to Git

```bash
git add .
git commit -m "Prepare for HostAfrica deployment"
git push origin dev
```

---

## 🚀 PHASE 3: UPLOAD TO HOSTAFRICA

### Step 3.1: Access HostAfrica cPanel

1. Go to `https://your-hosting-ip:2083` or the URL HostAfrica provided
2. Log in with your cPanel credentials

### Step 3.2: Upload Your Project Files

**Option A: Using Git (Recommended - Easier)**

1. **Enable SSH** (if not already enabled)
   - In cPanel, look for "Terminal" or "SSH Access"
   - Enable it if available

2. **Open Terminal/SSH**
   - In cPanel, find "Terminal" or use an SSH client (PuTTY on Windows)
   - Connect using your cPanel credentials

3. **Navigate to your domain directory**
   ```bash
   cd ~/public_html
   # OR if you have a subdomain:
   cd ~/public_html/yourdomain.com
   ```

4. **Clone your repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git .
   # The dot (.) means clone into current directory
   ```

**Option B: Using cPanel File Manager**

1. **Open File Manager** in cPanel
2. **Navigate to** `public_html` folder
3. **Upload your project**
   - Click "Upload" button
   - Select all your project files (or zip them first)
   - Wait for upload to complete
4. **Extract** if you uploaded a zip file

---

## ⚙️ PHASE 4: SETUP ON SERVER

### Step 4.1: Access Server via SSH/Terminal

1. **Open Terminal** in cPanel or use SSH client
2. **Navigate to your project**
   ```bash
   cd ~/public_html/your-project-name
   # Or wherever you uploaded your files
   ```

### Step 4.2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 4.3: Install Dependencies

```bash
# Make sure you're in the project directory and venv is activated
pip install --upgrade pip
pip install -r requirements.txt
```

**Wait for installation to complete** (may take a few minutes)

### Step 4.4: Set Up Database

1. **Create Database in cPanel**
   - Go to cPanel → "MySQL Databases" or "PostgreSQL Databases"
   - Click "Create Database"
   - Name it (e.g., `yourdomain_db`)
   - Click "Create Database"

2. **Create Database User**
   - In same page, scroll to "MySQL Users" or "PostgreSQL Users"
   - Create new user (e.g., `yourdomain_user`)
   - Set a strong password
   - Click "Create User"

3. **Add User to Database**
   - Scroll to "Add User to Database"
   - Select user and database
   - Click "Add"
   - Check "ALL PRIVILEGES"
   - Click "Make Changes"

4. **Note down credentials:**
   - Database name: `yourdomain_db`
   - Database user: `yourdomain_user`
   - Database password: `your_password`
   - Database host: Usually `localhost`

### Step 4.5: Update Database Settings

1. **Create `.env` file** in your project root:
   ```bash
   cd ~/public_html/your-project-name
   nano .env
   ```

2. **Add these lines** (replace with your actual values):
   ```env
   SECRET_KEY=your-generated-secret-key-from-step-2.1
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   
   # Database (PostgreSQL example - adjust if using MySQL)
   DATABASE_NAME=yourdomain_db
   DATABASE_USER=yourdomain_user
   DATABASE_PASSWORD=your_database_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   
   # M-Pesa Production
   MPESA_ENV=production
   MPESA_CONSUMER_KEY=your-production-consumer-key
   MPESA_CONSUMER_SECRET=your-production-consumer-secret
   MPESA_SHORTCODE=your-production-shortcode
   MPESA_PASSKEY=your-production-passkey
   MPESA_CALLBACK_BASE_URL=https://yourdomain.com
   ```

3. **Save and exit:**
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

### Step 4.6: Update Database Configuration in settings.py

1. **Edit settings.py:**
   ```bash
   nano config/settings.py
   ```

2. **Find DATABASES section** (around line 70-80) and update:

   **For PostgreSQL:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('DATABASE_NAME', 'yourdomain_db'),
           'USER': os.environ.get('DATABASE_USER', 'yourdomain_user'),
           'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
           'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
           'PORT': os.environ.get('DATABASE_PORT', '5432'),
       }
   }
   ```

   **For MySQL:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DATABASE_NAME', 'yourdomain_db'),
           'USER': os.environ.get('DATABASE_USER', 'yourdomain_user'),
           'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
           'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
           'PORT': os.environ.get('DATABASE_PORT', '3306'),
       }
   }
   ```

3. **Save and exit** (`Ctrl + X`, `Y`, `Enter`)

### Step 4.7: Run Migrations

```bash
# Make sure venv is activated
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create admin username, email, password
```

### Step 4.8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This creates the `staticfiles` folder with all CSS, JS, and images.

### Step 4.9: Set File Permissions

```bash
# Make sure files are readable
chmod 644 manage.py
chmod 644 passenger_wsgi.py
chmod -R 755 staticfiles
chmod -R 755 media
```

---

## 🔒 PHASE 5: SSL & SECURITY

### Step 5.1: Install SSL Certificate

1. **In cPanel**, go to **"SSL/TLS"** or **"Let's Encrypt SSL"**
2. **Click "Install"** or **"Run AutoSSL"**
3. **Select your domain**
4. **Click "Install"**
5. **Wait for installation** (usually takes a few minutes)

### Step 5.2: Force HTTPS

1. **Edit settings.py:**
   ```bash
   nano config/settings.py
   ```

2. **Add these lines** at the end of the file:
   ```python
   # Security settings for production
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   X_FRAME_OPTIONS = 'DENY'
   ```

3. **Save and exit**

---

## ✅ PHASE 6: TESTING

### Step 6.1: Test Your Website

1. **Visit your domain:** `https://yourdomain.com`
2. **Check if it loads** - You should see your homepage
3. **Test admin panel:** `https://yourdomain.com/admin/`
   - Log in with superuser credentials you created

### Step 6.2: Test Key Features

1. **User Registration**
   - Go to registration page
   - Create a test account
   - Verify it works

2. **Subscription Flow**
   - Log in as test user
   - Go to subscription plans
   - Try to subscribe (don't complete payment yet)

3. **M-Pesa Callback**
   - Visit: `https://yourdomain.com/payments/mpesa/callback/`
   - Should not give 404 error (even if it shows error, that's OK - means route exists)

### Step 6.3: Test M-Pesa Payment (Real Test)

1. **Use a real phone number** (yours or test phone)
2. **Complete subscription purchase**
3. **Enter M-Pesa PIN** when prompted
4. **Verify payment completes** and subscription activates

---

## 🐛 TROUBLESHOOTING

### Problem: Site shows 500 Error

**Solution:**
```bash
# Check error logs
tail -f ~/logs/error_log

# Or check Django logs
python manage.py check --deploy
```

### Problem: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --noinput
chmod -R 755 staticfiles
```

### Problem: Database connection error

**Solution:**
- Double-check database credentials in `.env`
- Verify database user has proper permissions
- Check if database host is correct (might be different from localhost)

### Problem: M-Pesa callbacks not working

**Solution:**
- Verify SSL is installed and working
- Check `MPESA_CALLBACK_BASE_URL` is correct
- Test callback URL: `https://yourdomain.com/payments/mpesa/callback/`
- Check Daraja portal for callback logs

### Problem: Permission denied errors

**Solution:**
```bash
chmod 755 manage.py
chmod 755 passenger_wsgi.py
chmod -R 755 staticfiles
chmod -R 755 media
```

---

## 📞 GETTING HELP

- **HostAfrica Support:** Check their support portal or contact support
- **Django Docs:** https://docs.djangoproject.com/
- **Daraja Support:** support@safaricom.co.ke

---

## ✅ FINAL CHECKLIST

- [ ] Domain pointed to HostAfrica
- [ ] Files uploaded to server
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Database created and configured
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Superuser created
- [ ] SSL certificate installed
- [ ] Site loads at https://yourdomain.com
- [ ] Admin panel accessible
- [ ] M-Pesa credentials updated to production
- [ ] Test payment completed successfully

**Congratulations! Your site should now be live! 🎉**
