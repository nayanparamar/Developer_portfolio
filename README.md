# Portfolio Studio

A fresh full-stack personal portfolio website with:

- modern public portfolio landing page
- SQLite database persistence
- owner authentication
- admin CMS for editing site content
- project, experience, skill, and testimonial management
- contact form with stored messages
- zero-dependency Python backend for easy hosting

## Run locally

```bash
python server.py
```

Then open [http://127.0.0.1:4280](http://127.0.0.1:4280).

## First login

Register the first account from the admin panel on the site. The first registered user becomes the owner admin.

## What you can edit

- hero section
- about section
- social links
- featured stats
- projects
- experience timeline
- skills
- testimonials
- incoming contact messages

## Hosting

This app is hosting-friendly because it uses only Python standard library modules.

Good options:

- Render web service
- Railway service
- a VPS running `python server.py`
- Docker

Set these environment variables in production:

- `HOST=0.0.0.0`
- `PORT` from your host
- `SESSION_COOKIE_SECURE=true`

Health check endpoint:

- `/api/health`

## Deployment files

- `render.yaml` is included for Render
- `Procfile` is included for simple process-based hosts
- `railway.json` is included for Railway
- `Dockerfile` is included for container hosting

See `DEPLOYMENT.md` for full deployment steps and SQLite persistence notes.
