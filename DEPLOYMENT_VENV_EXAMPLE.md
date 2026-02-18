# Virtual Environment Deployment Example

This document shows **exactly** what virtual environment data and commands you'll need when deploying to HostAfrica.

---

## 📦 What You Need to Upload

### File: `requirements.txt`

This is the **ONLY** file you need for virtual environment setup. It contains all package dependencies.

**Location in your project:** `C:\Users\ADMIN\PycharmProjects\Adult\requirements.txt`

**What it contains:**
```
Django>=5.0.0,<6.0.0
Pillow>=10.0.0
stripe>=7.0.0
django-unfold>=0.78.0
python-dotenv>=1.0.0
requests>=2.31.0
psycopg2-binary>=2.9.9
whitenoise>=6.6.0
gunicorn>=20.1.0
... (and more)
```

**✅ This file is already in your project and ready to upload!**

---

## 🖥️ Example: Server Setup Process

Here's what you'll do on the HostAfrica server:

### Step 1: Connect to Server

```bash
# SSH into HostAfrica (via cPanel Terminal or PuTTY)
ssh yourusername@yourdomain.com
# OR use cPanel Terminal
```

### Step 2: Navigate to Your Project

```bash
cd ~/public_html
# OR if your project is in a subdirectory:
cd ~/public_html/yourdomain.com
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment (this creates a 'venv' folder)
python3 -m venv venv

# Expected output:
# (No output, but venv folder is created)
```

### Step 4: Activate Virtual Environment

```bash
# Activate the virtual environment
source venv/bin/activate

# Expected output:
# Your prompt changes to show (venv):
# (venv) yourusername@server:~/public_html$
```

### Step 5: Upgrade pip

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Expected output:
# Collecting pip
# Downloading pip-25.0.1-py3-none-any.whl (2.1 MB)
# Installing collected packages: pip
# Successfully installed pip-25.0.1
```

### Step 6: Install All Packages from requirements.txt

```bash
# Install all dependencies
pip install -r requirements.txt

# Expected output (this will take 2-5 minutes):
# Collecting Django>=5.0.0,<6.0.0
#   Downloading Django-5.2.10-py3-none-any.whl (8.2 MB)
# Collecting Pillow>=10.0.0
#   Downloading Pillow-12.1.0-cp310-cp310-linux_x86_64.whl (3.4 MB)
# Collecting stripe>=7.0.0
#   Downloading stripe-14.3.0-py3-none-any.whl (1.1 MB)
# ...
# Installing collected packages: asgiref, certifi, charset-normalizer, ...
# Successfully installed Django-5.2.10 Pillow-12.1.0 stripe-14.3.0 ...
```

**✅ After this step, all packages are installed in the virtual environment!**

### Step 7: Verify Installation

```bash
# Check Django version
python manage.py --version

# Expected output:
# 5.2.10

# List installed packages
pip list

# Expected output:
# Package                       Version
# ----------------------------- --------
# asgiref                       3.11.0
# Django                        5.2.10
# Pillow                        12.1.0
# stripe                        14.3.0
# ... (all your packages)
```

---

## 📋 Complete Example Session

Here's a **complete example** of what your terminal session will look like:

```bash
# 1. Connect and navigate
yourusername@server:~$ cd ~/public_html
yourusername@server:~/public_html$ 

# 2. Create virtual environment
yourusername@server:~/public_html$ python3 -m venv venv
yourusername@server:~/public_html$ 

# 3. Activate it
yourusername@server:~/public_html$ source venv/bin/activate
(venv) yourusername@server:~/public_html$ 

# 4. Upgrade pip
(venv) yourusername@server:~/public_html$ pip install --upgrade pip
Collecting pip
  Downloading pip-25.0.1-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
Successfully installed pip-25.0.1

# 5. Install requirements
(venv) yourusername@server:~/public_html$ pip install -r requirements.txt
Collecting Django>=5.0.0,<6.0.0
  Downloading Django-5.2.10-py3-none-any.whl (8.2 MB)
Collecting Pillow>=10.0.0
  Downloading Pillow-12.1.0-cp310-cp310-linux_x86_64.whl (3.4 MB)
...
Installing collected packages: asgiref, certifi, charset-normalizer, ...
Successfully installed Django-5.2.10 Pillow-12.1.0 stripe-14.3.0 ...

# 6. Verify
(venv) yourusername@server:~/public_html$ python manage.py --version
5.2.10

# 7. Continue with migrations
(venv) yourusername@server:~/public_html$ python manage.py migrate
Operations to perform:
  Apply all migrations: accounts, admin, auth, ...
Running migrations:
  Applying accounts.0001_initial... OK
  ...
```

---

## 🔑 Key Points

### What You DON'T Need to Upload:
- ❌ `.venv` folder (too large, platform-specific)
- ❌ `requirements-freeze.txt` (optional, for exact versions)
- ❌ `VENV_SETUP.md` (documentation only)

### What You DO Need:
- ✅ `requirements.txt` (the only file needed!)

### Virtual Environment Location on Server:
```
~/public_html/
├── venv/              # Created on server (NOT uploaded)
│   ├── bin/
│   ├── lib/
│   └── ...
├── manage.py
├── requirements.txt   # Uploaded from your computer
├── config/
├── accounts/
└── ...
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "python3: command not found"
**Solution:**
```bash
# Try:
python -m venv venv
# OR check Python version:
which python3
```

### Issue 2: "pip: command not found"
**Solution:**
```bash
# Make sure venv is activated:
source venv/bin/activate
# You should see (venv) in prompt
```

### Issue 3: "Permission denied"
**Solution:**
```bash
# Check file permissions:
ls -la requirements.txt
# Should be readable (644)
```

### Issue 4: "Package installation fails"
**Solution:**
```bash
# Upgrade pip first:
pip install --upgrade pip
# Then try again:
pip install -r requirements.txt
```

---

## 📊 Package Installation Time Estimate

- **Small project (10-20 packages):** 1-2 minutes
- **Medium project (20-40 packages):** 2-5 minutes
- **Large project (40+ packages):** 5-10 minutes

Your project has ~33 packages, so expect **2-5 minutes** for installation.

---

## ✅ Quick Checklist

Before deployment, make sure:

- [ ] `requirements.txt` exists in your project root
- [ ] `requirements.txt` is committed to Git (or ready to upload)
- [ ] You know how to access SSH/Terminal on HostAfrica
- [ ] You have Python 3.10+ available on the server

---

## 🎯 Summary

**For deployment, you only need:**
1. **`requirements.txt`** file (already in your project ✅)
2. **Commands to run on server:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

That's it! The virtual environment will be created fresh on the server using your `requirements.txt` file.
