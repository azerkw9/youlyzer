# Youlyzer — YouTube Analyzer

A Django-powered web application for downloading YouTube thumbnails (all qualities), generating storyboard images, viewing detailed video information, and exploring channel data.

## Features

- **Thumbnail Downloads**: Download video thumbnails in all available qualities (default, medium, high, standard, max resolution)
- **Storyboard Generation**: Generate 3×3 grid storyboards from video frames using ffmpeg + Pillow
- **Video Analytics**: View detailed video stats — views, likes, duration, tags, upload date
- **Channel Explorer**: View channel details, subscriber count, and browse latest uploads
- **Admin Dashboard**: Custom admin panel to manage ads and contact messages
- **Contact Form**: Public contact page with database-backed message storage

## Requirements

- Python 3.10+
- ffmpeg (system-wide)
- pip (Python package manager)

## Setup Instructions

### 1. Clone & Navigate

```bash
cd youlyzer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg (required for storyboard generation)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (change SECRET_KEY for production)
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## URLs

| Path | Description |
|------|-------------|
| `/` | Home page with YouTube URL input |
| `/results/video/?url=...` | Video analysis results |
| `/results/channel/?url=...` | Channel analysis results |
| `/about/` | About page |
| `/contact/` | Contact form |
| `/privacy/` | Privacy policy |
| `/admin-dashboard/` | Custom admin dashboard (staff only) |
| `/admin/` | Django built-in admin |

## Project Structure

```
youlyzer/
├── manage.py
├── requirements.txt
├── .env / .env.example
├── youlyzer/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── core/              # Main application
│   ├── models.py      # Ad, ContactMessage
│   ├── views.py       # Public views
│   ├── admin_views.py # Custom admin dashboard
│   ├── forms.py       # Forms
│   ├── utils.py       # YouTube data + storyboard utils
│   └── urls.py        # URL routing
├── templates/         # HTML templates
├── static/            # CSS assets
└── media/             # Uploaded & generated files
```

## Deployment Notes

- Set `DEBUG=False` in production
- Change `SECRET_KEY` to a secure random value
- Configure `ALLOWED_HOSTS` with your domain
- For media files in production, use WhiteNoise or S3
- Consider running behind Gunicorn + Nginx
