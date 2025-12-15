# Gancheng B&B Flask Application

A full-featured booking system for Gancheng B&B in Hualien, Taiwan with user authentication, database management, email notifications, and form validation.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
# Copy the example file
Copy-Item .env.example .env

# Edit .env and set:
# - SECRET_KEY (generate a secure random key)
# - Email settings (optional, for notifications)
```

### 3. Initialize Database
```bash
python init_db.py
```

This creates:
- 3 sample rooms (Mountain View Suite, Garden Room, Family Villa)
- Admin user: `admin@gangcheng.com` / `admin123` ⚠️ Change this password!

### 4. Run the Development Server
```bash
python app.py
```

The site will be available at `http://localhost:5000`

## Features

✅ **User Authentication**
- Registration with email/username/password
- Login/logout with session management
- Protected profile page

✅ **Booking System**
- Guest bookings (no login required)
- Logged-in user bookings (tracked in profile)
- Date validation (no past dates, checkout after checkin)
- Automatic price calculation
- Email confirmations

✅ **Contact Form**
- Form validation
- Email notifications
- Database storage

✅ **Database Models**
- Users (with password hashing)
- Rooms (with pricing and amenities)
- Bookings (with status tracking)
- Contact messages

✅ **Email Integration**
- Booking confirmations
- Contact form notifications
- Configurable SMTP settings

## Project Structure
```
gangcheng/
├── app.py                     # Flask app with routes & API endpoints
├── models.py                  # Database models (User, Room, Booking, Contact)
├── forms.py                   # WTForms (validation for all forms)
├── init_db.py                 # Database initialization script
├── templates/
│   ├── index.html            # Homepage
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   └── profile.html          # User profile with bookings
├── static/                    # Static assets (currently unused - using CDN)
├── instance/
│   └── gangcheng.db          # SQLite database (auto-created)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create from .env.example)
└── .github/
    └── copilot-instructions.md
```

## Available Routes

### Pages
- `GET /` - Homepage with all sections
- `GET /login` - User login page
- `GET /register` - User registration page  
- `GET /profile` - User profile with bookings (requires login)
- `GET /logout` - Logout (requires login)

### API Endpoints
- `GET /api/rooms` - JSON list of available rooms
- `POST /api/contact` - Submit contact form
- `POST /api/booking` - Create booking

## Email Configuration

To enable email notifications:

1. **For Gmail:**
   - Enable 2-Factor Authentication
   - Generate App Password at https://myaccount.google.com/apppasswords
   - Add to `.env`:
     ```
     MAIL_USERNAME=your-email@gmail.com
     MAIL_PASSWORD=your-app-password
     MAIL_DEFAULT_SENDER=noreply@gangcheng.com
     ```

2. **For Other SMTP Servers:**
   - Update `.env` with your SMTP settings

## Development Notes

- Flask runs in **debug mode** by default (`debug=True` in app.py)
- Database auto-creates tables on first run
- Changes to templates refresh automatically
- **CSRF protection** enabled for forms, disabled for API endpoints

## Security Checklist for Production

⚠️ Before deploying:

1. ✅ Change `SECRET_KEY` in `.env` to a strong random value
2. ✅ Change admin password from default `admin123`
3. ✅ Set `FLASK_ENV=production`
4. ✅ Use PostgreSQL instead of SQLite
5. ✅ Set up proper SMTP email credentials
6. ✅ Use a production WSGI server (gunicorn, waitress)
7. ✅ Configure HTTPS/SSL

## Testing

All core features tested and working:
- ✅ Room listing API
- ✅ Contact form submission with validation
- ✅ Booking creation with price calculation
- ✅ User registration and login
- ✅ Profile page with booking history
