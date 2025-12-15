# Railway Deployment Guide

## Quick Deploy to Railway

### 1. Prerequisites
- GitHub account with your repository
- Railway account (sign up at https://railway.app)

### 2. Deploy Steps

#### Option A: Deploy from GitHub (Recommended)
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `maxim1976/demo-bnb`
4. Railway will auto-detect Flask and deploy

#### Option B: Deploy with Railway CLI
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### 3. Add PostgreSQL Database
1. In your Railway project dashboard, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable

### 4. Configure Environment Variables
In Railway project settings → Variables, add:

**Required:**
```
SECRET_KEY=your-super-secret-key-here-change-this
```

**Optional (for email notifications):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_DEFAULT_SENDER=noreply@gangcheng.com
```

### 5. Initialize Database
After first deployment, run once via Railway CLI or dashboard:
```bash
railway run python init_db.py
```

Or use Railway's "One-off Command" feature in the dashboard.

### 6. Access Your App
Railway provides a URL like: `https://demo-bnb-production.up.railway.app`

### 7. Important Post-Deployment Steps

**Change default admin password:**
1. Login with `admin@gangcheng.com` / `admin123`
2. Change password immediately in production

**Enable custom domain (optional):**
- Railway Settings → Domains → Add custom domain
- Point your DNS to Railway's provided address

## Railway Configuration Files

- **`Procfile`**: Tells Railway to use Gunicorn
- **`runtime.txt`**: Specifies Python version
- **`railway.json`**: Railway-specific configuration
- **`requirements.txt`**: Includes `gunicorn` and `psycopg2-binary` for PostgreSQL

## Database Migration

The app auto-creates tables on first run. For production data:

**From SQLite to PostgreSQL:**
```bash
# Export from local SQLite
python
>>> from app import app, db, Room, User, Booking, Contact
>>> with app.app_context():
>>>     rooms = Room.query.all()
>>>     # Manually recreate in Railway PostgreSQL
```

Or use init_db.py to create fresh sample data on Railway.

## Monitoring & Logs

- **Logs**: Railway Dashboard → Deployments → View Logs
- **Metrics**: Railway Dashboard → Metrics tab
- **Database**: Railway Dashboard → PostgreSQL → Data tab

## Troubleshooting

**Build fails:**
- Check `requirements.txt` versions
- Verify Python version in `runtime.txt`

**Database connection error:**
- Ensure PostgreSQL is added to project
- Check `DATABASE_URL` variable is set

**App crashes:**
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure `init_db.py` was run once

**CSRF errors:**
- Set proper `SECRET_KEY` in environment variables
- Check if deployed URL matches expected domain

## Cost Estimate

Railway free tier includes:
- $5 free credit per month
- Suitable for small projects
- PostgreSQL database included
- Custom domains supported

Typical usage: ~$5-10/month for small B&B site.

## Security Checklist for Production

- [ ] Change admin password from default
- [ ] Set strong `SECRET_KEY` 
- [ ] Use environment variables (never commit secrets)
- [ ] Enable HTTPS (Railway provides free SSL)
- [ ] Configure CORS if needed
- [ ] Set up database backups (Railway PostgreSQL backups)
- [ ] Monitor error logs regularly

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/maxim1976/demo-bnb/issues
