# Firebase Static Hosting

This repository is now ready for the no-payment Firebase Hosting path.

Firebase will publish only the `static/` folder. The portfolio works as a polished public website, and the contact form opens an email draft to `nayanparamar7@gmail.com`.

## What Works On Free Static Hosting

- public portfolio website
- responsive UI and animations
- project, experience, skill, and testimonial sections
- contact form via email draft
- GitHub Pages-like Firebase Hosting deployment

## What Is Disabled On Static Hosting

- admin login
- database-backed CMS edits
- saved contact messages
- Python API routes

Those backend features are still kept in the repo for later. To use them in production, deploy the Python server to a backend host and use persistent storage.

## Deploy Steps

Install Firebase CLI:

```bash
npm install -g firebase-tools
```

Login:

```bash
firebase login
```

Initialize or select your Firebase project:

```bash
firebase use --add
```

Deploy hosting:

```bash
firebase deploy --only hosting
```

Your site will be available at:

```text
https://YOUR_PROJECT_ID.web.app
https://YOUR_PROJECT_ID.firebaseapp.com
```

## Later Backend Upgrade

If you later want database, auth, CMS, and stored messages online, use one of these:

- Render or Railway with persistent storage
- Firebase Hosting plus Cloud Run plus Firestore
- VPS with the Python app and persistent disk

For a proper Firebase-native backend, migrate SQLite to Firestore before using Cloud Run.
