# Firebase Deployment

Firebase Hosting alone is not enough for this app because the portfolio has a Python backend, admin auth, SQLite storage, and contact-message APIs.

Use this Firebase architecture:

- Firebase Hosting for the public `web.app` / custom-domain URL
- Cloud Run for the Python app container
- Firestore or Cloud SQL for long-term production data

## Important Database Note

The current app uses SQLite. That is fine locally and works well on hosts with persistent disks, such as Render.

Cloud Run containers have an ephemeral filesystem. If you deploy the current SQLite version to Cloud Run as-is, admin edits and contact messages can be lost when the container restarts.

For a proper Firebase-native production setup, migrate the database layer to Firestore.

## Quick Cloud Run + Firebase Hosting Path

Install tools:

```bash
npm install -g firebase-tools
```

Install Google Cloud CLI:

```text
https://cloud.google.com/sdk/docs/install
```

Login:

```bash
firebase login
gcloud auth login
```

Set your project:

```bash
gcloud config set project YOUR_PROJECT_ID
firebase use YOUR_PROJECT_ID
```

Enable Cloud Run and Artifact Registry:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

Build and deploy the container:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/portfolio-studio
gcloud run deploy portfolio-studio --image gcr.io/YOUR_PROJECT_ID/portfolio-studio --region asia-south1 --allow-unauthenticated
```

Set production environment variables on Cloud Run:

```bash
gcloud run services update portfolio-studio --region asia-south1 --set-env-vars HOST=0.0.0.0,SESSION_COOKIE_SECURE=true
```

Deploy Firebase Hosting rewrite:

```bash
firebase deploy --only hosting
```

Your app will be available at:

```text
https://YOUR_PROJECT_ID.web.app
https://YOUR_PROJECT_ID.firebaseapp.com
```

## Recommended Next Upgrade

Before using Firebase as the final production host, replace SQLite with Firestore so:

- admin edits persist across deploys and restarts
- contact messages are stored reliably
- the app becomes Firebase-native
