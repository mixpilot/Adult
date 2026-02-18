# .env File Setup for Deployment

This guide shows you **exactly** what `.env` file data you need for deployment to HostAfrica.

---

## 📋 What is `.env` File?

The `.env` file contains **sensitive configuration data** that should NOT be committed to Git. It includes:
- Database credentials
- Secret keys
- API keys (M-Pesa, Stripe)
- Production settings

**⚠️ IMPORTANT:** Never commit `.env` to Git! It's already in `.gitignore`.

---

## 📝 Complete `.env` Template for Production

Create a file named `.env` in your project root with this content:

```env
# ============================================
# DJANGO SETTINGS
# ============================================
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# ============================================
# SESSION SECURITY (HTTPS)
# ============================================
SESSION_COOKIE_SECURE=True

# ============================================
# M-PESA DARAJA API (PRODUCTION)
# ============================================
MPESA_ENV=production
MPESA_CONSUMER_KEY=your_production_consumer_key
MPESA_CONSUMER_SECRET=your_production_consumer_secret
MPESA_SHORTCODE=your_production_shortcode
MPESA_PASSKEY=your_production_passkey
MPESA_CALLBACK_BASE_URL=https://yourdomain.com

# ============================================
# STRIPE (OPTIONAL - if using Stripe)
# ============================================
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

---

## 🔑 How to Get Each Value

### 1. SECRET_KEY

**Generate a new secret key:**

```bash
# On your local computer:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example output:**
```
django-insecure-abc123xyz789-def456ghi012-jkl345mno678-pqr901stu234
```

**Copy this and use it as your SECRET_KEY**

---

### 2. DEBUG and ALLOWED_HOSTS

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Replace `yourdomain.com` with your actual domain:**
- If your domain is `example.com` → `ALLOWED_HOSTS=example.com,www.example.com`
- If you have subdomain → `ALLOWED_HOSTS=app.example.com`

---

### 3. Database Configuration

**Get from HostAfrica cPanel:**

1. **Log into cPanel**
2. **Go to:** "MySQL Databases" or "PostgreSQL Databases"
3. **Create Database:**
   - Database name: `yourdomain_db` (note the full name, e.g., `username_yourdomain_db`)
   - Copy the **full database name**

4. **Create Database User:**
   - Username: `yourdomain_user` (note the full name, e.g., `username_yourdomain_user`)
   - Password: Create a strong password
   - Copy the **full username** and **password**

5. **Add User to Database:**
   - Select user and database
   - Grant ALL PRIVILEGES
   - Click "Make Changes"

**Example values:**
```env
DATABASE_ENGINE=django.db.backends.postgresql
# OR for MySQL: django.db.backends.mysql

DATABASE_NAME=username_yourdomain_db
DATABASE_USER=username_yourdomain_user
DATABASE_PASSWORD=MyStr0ng!P@ssw0rd
DATABASE_HOST=localhost
DATABASE_PORT=5432
# PostgreSQL: 5432
# MySQL: 3306
```

---

### 4. SESSION_COOKIE_SECURE

```env
SESSION_COOKIE_SECURE=True
```

**Always set to `True` in production** (after SSL is installed).

---

### 5. M-Pesa Daraja API Credentials

**Get from Safaricom Daraja Portal:**

1. **Go to:** https://developer.safaricom.co.ke/
2. **Log in** with your account
3. **Navigate to your app** (or create production app)
4. **Copy these values:**

   - **Consumer Key** (remove any spaces!)
   - **Consumer Secret** (remove any spaces!)
   - **Shortcode** (Paybill or Till number)
   - **Passkey**

**Example:**
```env
MPESA_ENV=production
MPESA_CONSUMER_KEY=TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTzF7Bzab3uuiUwH
MPESA_CONSUMER_SECRET=ws93rCpBMO9EyUJr16LmGAyXA4bEY0GA3lWiPWaqosf66NsgRzBGgIN7weR6q4hQ
MPESA_SHORTCODE=123456
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_BASE_URL=https://yourdomain.com
```

**⚠️ Important:**
- Remove ALL spaces from Consumer Key and Secret
- Use your **production** credentials (not sandbox)
- `MPESA_CALLBACK_BASE_URL` must be your actual domain with HTTPS

---

### 6. Stripe (Optional)

**Only if you're using Stripe payments:**

1. **Log into Stripe Dashboard:** https://dashboard.stripe.com/
2. **Go to:** Developers → API keys
3. **Switch to "Live mode"** (toggle in top right)
4. **Copy:**
   - Publishable key (starts with `pk_live_`)
   - Secret key (starts with `sk_live_`)
   - Webhook secret (from Webhooks section)

```env
STRIPE_PUBLISHABLE_KEY=pk_live_51AbC123...
STRIPE_SECRET_KEY=sk_live_51XyZ789...
STRIPE_WEBHOOK_SECRET=whsec_abc123def456...
```

---

## 📤 How to Create `.env` on Server

### Option 1: Using SSH/Terminal (Recommended)

```bash
# 1. SSH into HostAfrica server
ssh yourusername@yourdomain.com

# 2. Navigate to project directory
cd ~/public_html
# OR
cd ~/public_html/yourdomain.com

# 3. Create .env file
nano .env
# OR
vi .env

# 4. Paste your .env content (copy from template above)
# 5. Save and exit:
#    - Nano: Ctrl+X, then Y, then Enter
#    - Vi: Press Esc, type :wq, press Enter

# 6. Set proper permissions (important for security)
chmod 600 .env
```

### Option 2: Using cPanel File Manager

1. **Log into cPanel**
2. **Go to:** File Manager
3. **Navigate to:** `public_html` (or your project folder)
4. **Click:** "New File"
5. **Name it:** `.env` (with the dot at the beginning)
6. **Right-click** → "Edit"
7. **Paste** your `.env` content
8. **Save**

---

## ✅ Complete Example `.env` File

Here's a **real example** (with placeholder values you'll replace):

```env
# Django Settings
SECRET_KEY=django-insecure-abc123xyz789-def456ghi012-jkl345mno678-pqr901stu234
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com

# Database (PostgreSQL example)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=username_example_db
DATABASE_USER=username_example_user
DATABASE_PASSWORD=MyStr0ng!P@ssw0rd123
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Security
SESSION_COOKIE_SECURE=True

# M-Pesa Production
MPESA_ENV=production
MPESA_CONSUMER_KEY=TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTzF7Bzab3uuiUwH
MPESA_CONSUMER_SECRET=ws93rCpBMO9EyUJr16LmGAyXA4bEY0GA3lWiPWaqosf66NsgRzBGgIN7weR6q4hQ
MPESA_SHORTCODE=123456
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_BASE_URL=https://example.com
```

---

## 🔒 Security Checklist

- [ ] `.env` file is in `.gitignore` (already done ✅)
- [ ] `.env` file permissions set to `600` (only owner can read/write)
- [ ] All production credentials are from production sources (not sandbox/test)
- [ ] `DEBUG=False` in production
- [ ] Strong database password (mix of letters, numbers, symbols)
- [ ] `SECRET_KEY` is unique and randomly generated
- [ ] `SESSION_COOKIE_SECURE=True` (after SSL is installed)

---

## 🚨 Common Mistakes

### ❌ Mistake 1: Spaces in M-Pesa Credentials
```env
# WRONG:
MPESA_CONSUMER_KEY=TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTz F7Bzab3uuiUwH

# CORRECT:
MPESA_CONSUMER_KEY=TGmqAz7jqABXKbkzDvnVHhxhqaExuS21pTzF7Bzab3uuiUwH
```

### ❌ Mistake 2: Using Sandbox Credentials in Production
```env
# WRONG:
MPESA_ENV=sandbox
MPESA_SHORTCODE=174379

# CORRECT:
MPESA_ENV=production
MPESA_SHORTCODE=123456
```

### ❌ Mistake 3: Wrong Domain in ALLOWED_HOSTS
```env
# WRONG:
ALLOWED_HOSTS=localhost,127.0.0.1

# CORRECT:
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### ❌ Mistake 4: DEBUG=True in Production
```env
# WRONG:
DEBUG=True

# CORRECT:
DEBUG=False
```

---

## 📋 Quick Checklist

Before deployment, make sure you have:

- [ ] Generated new `SECRET_KEY`
- [ ] Database created in cPanel
- [ ] Database username and password
- [ ] Production M-Pesa credentials from Daraja portal
- [ ] Your domain name ready
- [ ] `.env` file created on server with all values filled in
- [ ] `.env` file permissions set to `600`

---

## 🎯 Summary

**What you need:**
1. **`.env` file** with all the variables above
2. **Values from:**
   - Django secret key generator
   - HostAfrica cPanel (database)
   - Safaricom Daraja portal (M-Pesa)
   - Your domain registrar (domain name)

**Where to create it:**
- On the server: `~/public_html/.env`
- Or in your project root on server

**File already created:** `env.example` (template file - copy and fill in your values)

---

## 📞 Need Help?

If you're stuck:
1. Check that all values are filled (no placeholders)
2. Verify no spaces in M-Pesa credentials
3. Make sure database exists in cPanel
4. Check file permissions: `chmod 600 .env`
5. Verify domain matches in `ALLOWED_HOSTS` and `MPESA_CALLBACK_BASE_URL`
