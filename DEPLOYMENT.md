# Deployment Guide (Render)

This guide helps you deploy the FastAPI backend to [Render](https://render.com).

## Prerequisites
1. A Render account.
2. The code pushed to a GitHub/GitLab repository.
3. A database (MySQL or Postgres).

## Deployment Steps

### Method 1: Blueprint Deployment (Recommended)
1. In your Render Dashboard, click **New +** and select **Blueprint**.
2. Connect your repository.
3. Render will use the `render.yaml` file to set up the service.
4. Go to the **Environment** tab in your service dashboard and set the following:
   - `DATABASE_URL`: Your production database connection string.
   - `GOOGLE_MAPS_API_KEY`: Your actual Google Maps API key.

### Method 2: Manual Web Service
1. Click **New +** -> **Web Service**.
2. Connect your repository.
3. Settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
4. Add environment variables in the **Environment** tab.

## Database Note
Render supports managed **PostgreSQL**. If you use Render's Postgres, update your `DATABASE_URL` to the Postgres connection string. The code is compatible with both MySQL and Postgres via SQLAlchemy.
