# Deployment Guide for Render

This guide will walk you through deploying the Jacobi Heat Simulation Web App to Render.

## Prerequisites

1. A GitHub account
2. A Render account (free tier is fine): https://render.com
3. This repository pushed to GitHub

## Step 1: Push to GitHub

If you haven't already, push this project to GitHub:

```bash
cd /Users/maarten/SVVR/Assignment1/SVVR/Assignment2/webapp
git init
git add .
git commit -m "Initial commit - Jacobi Heat Simulation Web App"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Step 2: Deploy Using Render Blueprint

### Option A: One-Click Blueprint Deployment (Recommended)

1. Go to https://dashboard.render.com/
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account if you haven't already
4. Select your repository
5. Render will detect the `render.yaml` file
6. Click **"Apply"**
7. Wait for both services to deploy (this may take 5-10 minutes)

That's it! Render will automatically:
- Deploy the backend Python service
- Deploy the frontend static site
- Link them together via environment variables

### Option B: Manual Deployment

If you prefer manual control:

#### Deploy Backend First

1. Go to https://dashboard.render.com/
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `jacobi-backend` (or your choice)
   - **Root Directory**: `Assignment2/webapp/backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app`
   - **Instance Type**: Free
5. **Add Environment Variable** (if needed):
   - None required for basic setup
6. Click **"Create Web Service"**
7. **Important**: Copy the service URL (e.g., `https://jacobi-backend.onrender.com`)

#### Deploy Frontend

1. Go to https://dashboard.render.com/
2. Click **"New"** → **"Static Site"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `jacobi-frontend` (or your choice)
   - **Root Directory**: `Assignment2/webapp/frontend`
   - **Branch**: `main`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`
5. **Add Environment Variable**:
   - **Key**: `REACT_APP_BACKEND_URL`
   - **Value**: The backend URL from step 1.7 (e.g., `https://jacobi-backend.onrender.com`)
6. Click **"Create Static Site"**

## Step 3: Verify Deployment

1. Once both services show "Live" status, open the frontend URL
2. You should see the welcome screen
3. Enter hot-square sizes and click "Run Simulations"
4. Verify that:
   - WebSocket connects (check browser console)
   - Simulations run
   - Frames appear in real-time
   - Convergence plot updates

## Step 4: Custom Domain (Optional)

### For Frontend:
1. In your frontend service settings, go to "Custom Domains"
2. Click "Add Custom Domain"
3. Follow Render's instructions to configure DNS

### For Backend:
1. In your backend service settings, go to "Custom Domains"
2. Add your API subdomain (e.g., `api.yourdomain.com`)
3. Update the frontend environment variable `REACT_APP_BACKEND_URL` to use your custom domain

## Troubleshooting

### Backend Issues

**Service won't start:**
- Check the logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python version is 3.9+

**WebSocket connection fails:**
- Check CORS settings in `app.py`
- Verify the frontend is using the correct backend URL
- Check browser console for errors

### Frontend Issues

**Blank page:**
- Check build logs for errors
- Verify `REACT_APP_BACKEND_URL` is set correctly
- Clear browser cache

**Can't connect to backend:**
- Verify backend is running and healthy (`/health` endpoint)
- Check CORS configuration
- Ensure environment variable is correct

### Performance Issues

**Simulations run slowly:**
- This is expected on free tier (limited CPU)
- Consider upgrading to a paid instance type
- Reduce grid size or output frequency

## Monitoring

- **Health Check**: Both services have health check endpoints
- **Logs**: Available in Render dashboard for each service
- **Metrics**: View CPU/Memory usage in dashboard

## Updating the App

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update message"
   git push
   ```
3. Render will automatically detect the push and redeploy

## Cost Estimates

- **Free Tier**: Both services can run on free tier
  - Backend: 750 free hours/month
  - Frontend: Unlimited bandwidth on static sites
  - Note: Free services may spin down after inactivity

- **Paid Tier**: Starting at $7/month per service
  - No spin-down
  - Better performance
  - More resources

## Support

If you encounter issues:
1. Check Render's status page: https://status.render.com/
2. Review Render's documentation: https://render.com/docs
3. Check the application logs in the Render dashboard
4. Review browser console for frontend errors

## Security Notes

- Backend includes CORS configuration for security
- WebSocket connections use secure protocols in production
- No sensitive data is stored or transmitted
- All communication over HTTPS

---

**Congratulations!** Your Jacobi Heat Simulation Web App is now deployed! 🎉

