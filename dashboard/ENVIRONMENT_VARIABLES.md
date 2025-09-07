# Environment Variables Configuration

## Current Configuration

The project is currently configured to use the following environment variables:

### Frontend (Next.js)
- **NEXT_PUBLIC_API_URL**: `http://127.0.0.1:5000/api`
  - Used in: `dashboard/lib/api.ts`
  - Purpose: Base URL for API calls to the Flask backend
  - Default: `http://127.0.0.1:5000/api`

### Backend (Flask)
- **Host**: `127.0.0.1` (configured in `dashboard/config.json`)
- **Port**: `5000` (configured in `dashboard/config.json`)
- **Debug**: `true` (configured in `dashboard/config.json`)

## How to Configure Environment Variables

### Option 1: Using .env.local file (Recommended)
Create a file named `.env.local` in the `dashboard` folder with:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api
```

### Option 2: Using system environment variables
Set the environment variable in your system:
```bash
# Windows (PowerShell)
$env:NEXT_PUBLIC_API_URL="http://127.0.0.1:5000/api"

# Windows (Command Prompt)
set NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api

# Linux/Mac
export NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api
```

### Option 3: Using next.config.ts (Current)
The configuration is already set in `dashboard/next.config.ts` with fallback values.

## Verification

To verify the configuration is working:

1. **Check API calls**: Open browser developer tools and look for API calls to `http://127.0.0.1:5000/api`
2. **Check console logs**: The API service logs the URL being used
3. **Test endpoints**: Use curl or browser to test `http://127.0.0.1:5000/api/status`

## Troubleshooting

If you're having issues:

1. **CORS errors**: Make sure Flask CORS is configured for your frontend URL
2. **Connection refused**: Ensure Flask server is running on the correct port
3. **Wrong URL**: Check that `NEXT_PUBLIC_API_URL` is set correctly
4. **Cache issues**: Clear browser cache and restart Next.js dev server

## Current Status: ✅ WORKING

The current configuration is working correctly with:
- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:5000`
- API calls: `http://127.0.0.1:5000/api/*`
