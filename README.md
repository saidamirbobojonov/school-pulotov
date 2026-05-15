# School Pulatov — School Website

A full-featured school website built with Django. Designed for portfolio and demo purposes.

## Tech Stack

- **Backend**: Django 5.2
- **Admin Panel**: django-unfold (custom branded admin)
- **Translations**: django-modeltranslation (Tajik, Russian, English)
- **Static Files**: WhiteNoise
- **Database**: SQLite (demo) / PostgreSQL (production)
- **Deployment**: Railway

## Features

- Multilingual support (Tajik / Russian / English)
- Custom admin dashboard with django-unfold
- News and announcements
- Events (school & extracurricular)
- Academic programs
- Clubs and competitions
- Staff/people directory
- Contact form with rate limiting
- Site content management

## Run Locally

```bash
git clone <your-repo-url>
cd school-pulotov

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create a .env file (see .env.example below)
cp .env.example .env  # then edit it

python manage.py migrate
python manage.py runserver
```

### .env example

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SERVE_STATICFILES=True
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Deploy on Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Select this repository
4. Add environment variables in Railway dashboard:
   - `SECRET_KEY` → generate a secure key (see command above)
   - `DEBUG` → `False`
5. Railway will auto-detect Python, install dependencies, and run the Procfile

The `db.sqlite3` file is committed so the demo data is available immediately after deploy.

> **Note:** Railway's filesystem is ephemeral — any data added via the admin panel will reset on the next deploy. This is fine for a portfolio demo.

## Admin Panel

Visit `/admin` to access the custom admin dashboard. Create a superuser locally:
```bash
python manage.py createsuperuser
```
