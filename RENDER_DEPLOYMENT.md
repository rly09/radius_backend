# Render Deployment Instructions - Smart Service Finder Backend

Follow these steps to deploy your backend to [Render](https://render.com/).

## 1. Create a Render Account
If you haven't already, sign up at [Render](https://dashboard.render.com/).

## 2. Connect Your GitHub Repository
1. Click **New +** and select **Web Service**.
2. Connect your GitHub/GitLab account and select your `smart_service_finder` repository.

## 3. Configure the Web Service
- **Name**: `smart-service-finder-backend` (or your choice)
- **Root Directory**: `backend`
- **Environment**: `Docker`
- **Instance Type**: `Free` (or higher)

## 4. Set Environment Variables (Secrets)
Go to the **Environment** tab on your Render dashboard and add:

| Key | Value |
|---|---|
| `DATABASE_URL` | your_neon_database_url |
| `GOOGLE_MAPS_API_KEY` | your_google_maps_api_key |

> [!IMPORTANT]
> The `DATABASE_URL` should be the same Neon link you provided:
> `postgresql://neondb_owner:npg_ptdT06PSmwNy@ep-silent-pine-a1b7i5vb-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`

## 5. Deploy
Click **Create Web Service**. Render will build the Docker container and deploy it.

## 6. Update Frontend
Once deployed, copy the Render URL (e.g., `https://smart-service-finder-backend.onrender.com`) and update `lib/app_config.dart` in the `frontend` folder.
