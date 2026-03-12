# novel-it

A self-hosted web application for writing and planning novels. Built with Django,
HTMX, Alpine.js, and Tailwind CSS.

novel-it is free, open-source software. It exists as an alternative to
commercial web-based writing tools — you own your data, you run your own
instance, and no one is monetising your writing.

## Features

**Writing**
- Novels → Chapters → Scenes hierarchy
- Markdown editor with live preview and distraction-free mode
- Auto-save every 30 seconds
- Word count at scene, chapter, and novel level

**Planning**
- Character, location, and item databases, each scoped to a novel
- Image uploads for characters, locations, and items
- Entity scanning — characters, locations, and items mentioned in a scene
  are automatically detected and linked
- Relationship mapping between characters, locations, and items

**General**
- Multi-user support — each user sees only their own novels
- Soft delete with restore capability
- BDD test suite using Behave

## Requirements

- Python 3.10+
- pip

SQLite is used by default and requires no additional setup. PostgreSQL is
supported via the `DATABASE_URL` environment variable (see Configuration).

## Quick Start

```bash
git clone https://github.com/david-hollingworth/novel-it.git
cd novel-it/novelapp

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp ../.env.example .env
# Edit .env — at minimum set DJANGO_SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://localhost:8000 in your browser.

## Configuration

All configuration is via environment variables in a `.env` file. Copy
`.env.example` to `.env` and edit as needed.

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | *(required)* | Django secret key |
| `DJANGO_DEBUG` | `False` | Set to `True` for development |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Comma-separated list of trusted origins |
| `DATABASE_URL` | SQLite | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/novelapp` |

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Production Deployment

For a production deployment behind a reverse proxy (Caddy, Nginx, etc.):

1. Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS` appropriately
2. Collect static files: `python manage.py collectstatic`
3. Run with Gunicorn: `gunicorn novelapp.wsgi:application`
4. Serve `staticfiles/` and `media/` directories via your reverse proxy

Full installation guide: [docs/installation.md](docs/installation.md) *(coming soon)*

## Running Tests

```bash
python manage.py behave
```

## Licence

Copyright (C) 2025 David Hollingworth

novel-it is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

See [LICENSE](LICENSE) for the full licence text.
