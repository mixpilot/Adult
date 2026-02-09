# Adult Entertainment Website

A Django-based adult entertainment website with content management, user authentication, and media handling capabilities.

## Features

- **User Authentication**: Registration, login, logout, and user profiles
- **Content Management**: Upload and manage videos, images, and galleries
- **Categories & Tags**: Organize content with categories and tags
- **Search & Filtering**: Search content and filter by category, tags, and sorting options
- **Comments System**: Users can comment on content
- **Admin Panel**: Full Django admin interface for content management
- **Responsive Design**: Modern, mobile-friendly UI with Bootstrap 5

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd C:\Users\ADMIN\PycharmProjects\Adult
   ```

2. **Activate virtual environment (if using one):**
   ```bash
   pythonProject\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the website:**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
Adult/
├── config/              # Main project configuration
│   ├── settings.py      # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── accounts/            # User authentication app
│   ├── models.py        # Custom User model
│   ├── views.py         # Authentication views
│   └── forms.py         # User forms
├── content/             # Content management app
│   ├── models.py        # Content, Category, Tag models
│   ├── views.py         # Content views
│   └── admin.py         # Admin configuration
├── core/                # Core app (home page)
│   └── views.py         # Home view
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── core/            # Core templates
│   ├── accounts/        # Authentication templates
│   └── content/         # Content templates
├── static/              # Static files (CSS, JS, images)
│   └── css/
│       └── style.css    # Custom styles
├── media/               # User-uploaded media files (created automatically)
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Usage

### Creating Content

1. Log in to the admin panel at `/admin/`
2. Navigate to Content section
3. Add Categories and Tags first
4. Create Content entries with:
   - Title and description
   - Thumbnail image
   - Video file or video URL
   - Category and tags
   - Content type (video, image, or gallery)

### User Features

- **Registration**: Users can create accounts
- **Profile**: Users can update their profile information
- **Browse**: Users can browse all content with filtering options
- **View**: Users can view content details
- **Comment**: Authenticated users can comment on content

## Development Notes

- The project uses SQLite by default (change in `settings.py` for production)
- Media files are stored in the `media/` directory
- Static files are collected in `staticfiles/` when running `collectstatic`
- Change `SECRET_KEY` in `settings.py` before deploying to production
- Set `DEBUG = False` in production and configure `ALLOWED_HOSTS`

## Security Considerations

⚠️ **Important**: Before deploying to production:

1. Change the `SECRET_KEY` in `config/settings.py`
2. Set `DEBUG = False`
3. Configure proper `ALLOWED_HOSTS`
4. Use a production database (PostgreSQL recommended)
5. Set up proper media file serving (not via Django in production)
6. Implement HTTPS
7. Add rate limiting for uploads
8. Implement content moderation
9. Add age verification if required by law
10. Review and comply with local regulations regarding adult content

## License

This project is for educational purposes. Ensure compliance with all applicable laws and regulations in your jurisdiction.
