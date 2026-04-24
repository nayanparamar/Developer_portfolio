# Deployment Guide

This portfolio runs on the Python standard library and stores content in SQLite.

## Recommended: Render

1. Push the `portfolio-studio` folder to GitHub.
2. Create a new Render Web Service from that repository.
3. Use these settings:

```text
Runtime: Python
Build command: leave empty
Start command: python server.py
Health check path: /api/health
```

4. Add environment variables:

```text
HOST=0.0.0.0
SESSION_COOKIE_SECURE=true
DB_PATH=/var/data/portfolio_studio.db
```

5. Add a Render persistent disk mounted at:

```text
/var/data
```

The persistent disk matters because SQLite is a file database. Without it, admin edits and contact messages can disappear after redeploys.

## Railway

Use these environment variables:

```text
HOST=0.0.0.0
SESSION_COOKIE_SECURE=true
DB_PATH=./data/portfolio_studio.db
```

Start command:

```bash
python server.py
```

If Railway provides persistent volumes for your plan, point `DB_PATH` to that mounted volume.

## VPS

Clone or upload the project, then run:

```bash
cd portfolio-studio
python server.py
```

For production, run it behind Nginx or Caddy and set:

```text
HOST=127.0.0.1
SESSION_COOKIE_SECURE=true
```

Point your reverse proxy to the app port, default `4280`.

## First Admin Account

After deployment:

1. Open the live website.
2. Click `Admin`.
3. Register your first account.

The first registered account becomes the admin owner. After that, sign in from the same panel to edit your portfolio.

## Important Environment Variables

```text
HOST=0.0.0.0
PORT=4280
DB_PATH=./data/portfolio_studio.db
SESSION_COOKIE_SECURE=true
PBKDF2_ITERATIONS=310000
```

Most hosts set `PORT` automatically. If they do, leave it to the host.
