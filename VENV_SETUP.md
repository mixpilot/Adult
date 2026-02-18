# Virtual Environment Setup Guide

This guide explains how to set up and manage the virtual environment for this Django project.

## Current Environment Details

### Python Version
- **Recommended**: Python 3.10 or higher
- Check your version: `python --version`

### Installed Packages
The project uses the following main packages:
- **Django**: 5.2.10 (Web framework)
- **Pillow**: 12.1.0 (Image processing)
- **stripe**: 14.3.0 (Payment processing)
- **django-unfold**: 0.78.1 (Admin theme)
- **psycopg2-binary**: 2.9.11 (PostgreSQL adapter)
- **gunicorn**: 25.0.1 (Production server)
- **whitenoise**: 6.11.0 (Static files)
- **requests**: 2.32.5 (HTTP requests)
- **python-dotenv**: 1.2.1 (Environment variables)

See `requirements.txt` for all dependencies.

## Setting Up Virtual Environment

### Windows (PowerShell)

#### Step 1: Create Virtual Environment
```powershell
# Navigate to project directory
cd C:\Users\ADMIN\PycharmProjects\Adult

# Create virtual environment
python -m venv .venv
```

#### Step 2: Activate Virtual Environment
```powershell
# Activate
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install from requirements.txt
pip install -r requirements.txt

# OR install exact versions
pip install -r requirements-freeze.txt
```

#### Step 4: Verify Installation
```powershell
# Check installed packages
pip list

# Verify Django
python manage.py --version
```

### Windows (Command Prompt)

```cmd
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Linux/Mac

```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Virtual Environment Management

### Activating the Environment

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Deactivating the Environment

```bash
deactivate
```

### Updating Packages

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade Django

# Update requirements.txt after changes
pip freeze > requirements-freeze.txt
```

### Adding New Packages

```bash
# Install new package
pip install package-name

# Add to requirements.txt manually, or:
pip freeze > requirements-freeze.txt
```

## Project Structure

```
Adult/
├── .venv/              # Virtual environment (not in git)
├── accounts/           # User accounts app
├── config/             # Django settings
├── connections/        # Connections app
├── content/            # Content/Gallery app
├── core/               # Core app
├── payments/           # Payments app
├── subscriptions/      # Subscriptions app
├── static/             # Static files
├── templates/          # HTML templates
├── db.sqlite3          # SQLite database (dev)
├── manage.py           # Django management script
├── requirements.txt    # Package requirements (flexible versions)
├── requirements-freeze.txt  # Exact versions
└── VENV_SETUP.md      # This file
```

## Common Issues

### Issue 1: Execution Policy Error (PowerShell)
**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: Python Not Found
**Error**: `python: command not found`

**Solution**:
- Use `python3` instead of `python`
- Or add Python to PATH environment variable

### Issue 3: Package Installation Fails
**Error**: `ERROR: Could not find a version that satisfies the requirement`

**Solution**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Issue 4: Virtual Environment Not Activating
**Solution**:
- Make sure you're in the project directory
- Check that `.venv` folder exists
- Use full path: `C:\Users\ADMIN\PycharmProjects\Adult\.venv\Scripts\Activate.ps1`

## For Deployment (HostAfrica)

When deploying to production:

1. **Don't upload `.venv` folder** - it's too large and platform-specific
2. **Use `requirements.txt`** on the server
3. **Create fresh virtual environment** on the server:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Quick Reference

```powershell
# Create venv
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Check packages
pip list

# Deactivate
deactivate
```

## Notes

- The `.venv` folder should be in `.gitignore` (don't commit it)
- Always activate the virtual environment before running Django commands
- Use `requirements.txt` for flexible version requirements
- Use `requirements-freeze.txt` for exact version reproduction
