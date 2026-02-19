# HostAfrica Deployment Checklist

## Pre-Deployment

- [ ] Generate new `SECRET_KEY` for production
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Set `DEBUG = False` in production
- [ ] Get production M-Pesa credentials from Daraja portal
- [ ] Set up database (PostgreSQL or MySQL) in HostAfrica cPanel
- [ ] Purchase domain and point it to HostAfrica nameservers

## Files to Upload

- [ ] All project files (via Git or FTP)
- [ ] `passenger_wsgi.py` (created for you)
- [ ] `.htaccess` (created for you)
- [ ] `requirements.txt` (updated with all dependencies)

## Configuration

- [ ] Create `.env` file with production values
- [ ] Update database settings in `config/settings.py`
- [ ] Set `MPESA_ENV = 'production'`
- [ ] Update `MPESA_CALLBACK_BASE_URL` to your domain
- [ ] Configure email settings (if needed)

## Server Setup

- [ ] SSH into HostAfrica server
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Create superuser: `python manage.py createsuperuser`

## SSL & Security

- [ ] Install SSL certificate (Let's Encrypt via cPanel)
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Set `SECURE_SSL_REDIRECT = True`

## Testing

- [ ] Visit your domain - site loads correctly
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test subscription purchase flow
- [ ] Test M-Pesa payment (with real credentials)
- [ ] Verify M-Pesa callback is working
- [ ] Test file uploads (if applicable)
- [ ] Check static files are loading
- [ ] Check media files are accessible

## Post-Deployment

- [ ] Set up regular backups
- [ ] Monitor error logs
- [ ] Set up email notifications for errors (optional)
- [ ] Update DNS if needed
- [ ] Test from different devices/browsers

## Important URLs to Test

- Homepage: `https://yourdomain.com/`
- Admin: `https://yourdomain.com/admin/`
- M-Pesa Callback: `https://yourdomain.com/payments/mpesa/callback/`
- Subscription Plans: `https://yourdomain.com/subscriptions/plans/`

## Support Contacts

- HostAfrica Support: [Check their website]
- Daraja Support: support@safaricom.co.ke
