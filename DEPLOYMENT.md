## Fly.io Deployment
The backend is now configured to deploy via **Fly.io** using Docker.

### 1. Login to Fly.io
If the `fly` command is not recognized, use the full path: `~\ .fly\bin\flyctl.exe`
```powershell
# Using the full path in PowerShell
& "$Env:USERPROFILE\.fly\bin\flyctl.exe" auth login
```
Or restart your terminal to use just `fly`.

### 2. Initialize App (First time only)
```powershell
& "$Env:USERPROFILE\.fly\bin\flyctl.exe" launch
```
Choose your app name and region. When asked for "Do you want to tweak these settings?", you can say No or Yes to adjust.

### 3. Set Environment Variables
Go to the Fly.io dashboard or run:
```powershell
fly secrets set DATABASE_URL="your_neon_postgres_url" GOOGLE_MAPS_API_KEY="your_api_key"
```

### 4. Deploy
```powershell
fly deploy
```

## Important: Git Cleanup
I've removed the `venv/` folder from tracking and updated `.gitignore`. Please run:
```bash
git add .
git commit -m "Optimize for Render free tier and clean git"
git push origin main
```
