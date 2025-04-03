# Content Repurposer Deployment Guide

This guide provides instructions for deploying the Content Repurposer application to Vercel (frontend) and Render (backend).

## Frontend Deployment (Vercel)

### Prerequisites
- A [Vercel account](https://vercel.com)
- Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

### Deployment Steps

1. Login to [Vercel](https://vercel.com) and click "New Project"
2. Import your Git repository
3. Configure the project:
   - Framework Preset: Next.js
   - Root Directory: `frontend` (if your repo contains both frontend and backend code)
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
4. Under "Environment Variables", add the following:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend-url.onrender.com` (replace with your actual Render backend URL)
5. Click "Deploy"

## Backend Deployment (Render)

### Prerequisites
- A [Render account](https://render.com)
- Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

### Deployment Steps

1. Login to [Render](https://render.com) and click "New" > "Web Service"
2. Connect your Git repository
3. Configure the service:
   - Name: `content-repurposer-api` (or your preferred name)
   - Environment: Python 3
   - Root Directory: `backend` (if your repo contains both frontend and backend code)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Under "Environment Variables", add:
   - `GEMINI_API_KEY` = your actual Gemini API key
   - Any other environment variables from your `.env` file
5. Choose the free plan (or another plan if needed)
6. Click "Create Web Service"

## Connecting Frontend to Backend

### Update CORS Settings

After deploying your frontend to Vercel, you'll get a domain like `https://your-app.vercel.app`. Update your backend's CORS settings in `main.py` to allow requests from this domain:

```python
frontend_urls = [
    "https://your-app.vercel.app",  # Your Vercel domain
    "http://localhost:3000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,  # In production, use specific domains
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
```

Then redeploy your backend to Render for the changes to take effect.

### Test the Deployment

1. Visit your Vercel frontend URL
2. Try making a request to summarize content or create a social post
3. Check that the frontend can successfully communicate with the backend

## Troubleshooting

### Frontend Issues
- **API Connection Errors**: Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- **Build Errors**: Make sure all TypeScript types are properly defined

### Backend Issues
- **Application Errors**: Check Render logs for specific error messages
- **CORS Errors**: Verify your CORS settings include your frontend domain
- **API Key Issues**: Ensure the `GEMINI_API_KEY` is set correctly in environment variables

## Local Development After Deployment

To work locally but connect to your deployed backend:
1. Update your local `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

To work completely locally:
1. Use the default local settings:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
2. Run your backend locally: `cd backend && uvicorn main:app --reload`
3. Run your frontend locally: `cd frontend && npm run dev` 