# How to Fix "Not Secure" Warning - Enable HTTPS

Your site shows "Not secure" because it's using **HTTP** instead of **HTTPS**. Here's how to fix it:

---

## 🔒 **What is HTTPS?**

- **HTTP** = Unencrypted connection (shows "Not secure")
- **HTTPS** = Encrypted connection (shows secure padlock 🔒)

HTTPS encrypts data between the browser and your server, protecting user information.

---

## ✅ **Step 1: Install SSL Certificate on HostAfrica**

### **Option A: Using cPanel (Easiest)**

1. **Log into HostAfrica cPanel**
2. **Find "SSL/TLS"** or **"Let's Encrypt SSL"** section
3. **Click "Install"** or **"Run AutoSSL"**
4. **Select your domain:** `malisafiescorts.co.ke`
5. **Click "Install"** or **"Issue"**
6. **Wait 2-5 minutes** for installation

**Note:** Let's Encrypt is **FREE** and renews automatically.

### **Option B: Manual Installation**

If AutoSSL doesn't work:

1. Go to **"SSL/TLS"** → **"Manage SSL Sites"**
2. Select your domain
3. Choose **"Let's Encrypt"**
4. Click **"Run"** or **"Install"**

---

## ✅ **Step 2: Update Django Settings for HTTPS**

Add these settings to force HTTPS. Edit `config/settings.py`:

### **Add at the end of `config/settings.py`:**

```python
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
    
    # Prevent clickjacking
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

## ✅ **Step 3: Update .htaccess for HTTPS Redirect**

If you have an `.htaccess` file, add this at the top to force HTTPS:

```apache
# Force HTTPS
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>
```

**Location:** Add this to your `.htaccess` file in `public_html/`

---

## ✅ **Step 4: Update M-Pesa Callback URL**

Since you're now using HTTPS, update your M-Pesa callback URL:

**In your `.env` file or cPanel environment variables:**

```env
MPESA_CALLBACK_BASE_URL=https://malisafiescorts.co.ke
```

**Also update in `config/settings.py` if needed:**
- Make sure `MPESA_CALLBACK_BASE_URL` uses `https://` not `http://`

---

## ✅ **Step 5: Test HTTPS**

1. **Wait 5-10 minutes** after installing SSL
2. **Visit:** `https://malisafiescorts.co.ke` (note the `https://`)
3. **Check for padlock 🔒** in browser address bar
4. **Test redirect:** Visit `http://malisafiescorts.co.ke` - it should automatically redirect to `https://`

---

## 🔍 **Verification Checklist**

After completing the steps:

- [ ] SSL certificate installed in cPanel
- [ ] Django settings updated with HTTPS security settings
- [ ] `.htaccess` updated (if using)
- [ ] M-Pesa callback URL updated to `https://`
- [ ] Site loads with `https://` (padlock shows)
- [ ] HTTP redirects to HTTPS automatically
- [ ] No "Not secure" warning in browser

---

## 🐛 **Troubleshooting**

### **Problem: SSL installed but still shows "Not secure"**

**Solutions:**
1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Wait 10-15 minutes** - SSL propagation can take time
3. **Check SSL status** in cPanel → SSL/TLS → Manage SSL Sites
4. **Verify domain** is correctly pointing to HostAfrica nameservers

### **Problem: Site breaks after enabling HTTPS**

**Solutions:**
1. **Check `ALLOWED_HOSTS`** includes your domain:
   ```python
   ALLOWED_HOSTS = ['malisafiescorts.co.ke', 'www.malisafiescorts.co.ke']
   ```

2. **Check static files** - make sure they load over HTTPS:
   - Update any hardcoded `http://` URLs in templates
   - Use `{% load static %}` for static files

3. **Temporarily disable HTTPS redirect** to test:
   ```python
   SECURE_SSL_REDIRECT = False  # Set to False temporarily
   ```

### **Problem: Mixed Content Warnings**

If you see "Mixed Content" warnings:
- Some resources (images, CSS, JS) are still loading over HTTP
- Update all URLs in your templates to use `https://` or relative URLs
- Check browser console for which resources are causing issues

### **Problem: M-Pesa callbacks not working**

**Solutions:**
1. **Verify callback URL** is accessible:
   - Visit: `https://malisafiescorts.co.ke/payments/mpesa/callback/`
   - Should return 200 OK (not 404)

2. **Check Daraja portal:**
   - Log into https://developer.safaricom.co.ke/
   - Verify callback URL is set to `https://malisafiescorts.co.ke/payments/mpesa/callback/`

3. **Test with production credentials:**
   - Make sure you're using production Consumer Key/Secret
   - Sandbox credentials won't work with production domain

---

## 📝 **Quick Reference: Settings to Add**

Add this to the **end** of your `config/settings.py`:

```python
# HTTPS & Security (Production Only)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

## ⚡ **Quick Fix Summary**

1. **Install SSL** in HostAfrica cPanel (Let's Encrypt - free)
2. **Add HTTPS settings** to `config/settings.py` (see above)
3. **Update `.htaccess`** to force HTTPS redirect
4. **Update M-Pesa callback** to use `https://`
5. **Wait 5-10 minutes** and test

After this, your site will show a **secure padlock 🔒** instead of "Not secure"!

---

## 📞 **Need Help?**

- **HostAfrica Support:** Contact them if SSL installation fails
- **SSL Checker:** Use https://www.ssllabs.com/ssltest/ to verify your SSL
- **Browser DevTools:** Check Console tab for any HTTPS-related errors

---

**Once HTTPS is enabled, your site will be secure and trusted by browsers!** ✅
