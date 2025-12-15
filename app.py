from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from datetime import datetime, date
from functools import wraps
import os
from dotenv import load_dotenv

from models import db, User, Room, Booking, Contact
from forms import ContactForm, BookingForm, LoginForm, RegisterForm

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration - Railway provides DATABASE_URL for PostgreSQL
database_url = os.getenv('DATABASE_URL', 'sqlite:///gangcheng.db')
# Railway uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@gangcheng.com')

# Initialize extensions
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize WTForms CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# Disable CSRF for API endpoints
@csrf.exempt
def disable_csrf_for_api():
    """Disable CSRF for API routes"""
    pass


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Homepage with featured room listings"""
    rooms = Room.query.filter_by(is_available=True, is_featured=True).all()
    return render_template('index.html', rooms=rooms)


@app.route('/rooms')
def all_rooms():
    """All rooms page"""
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)


@app.route('/about')
def about():
    """About/Story page"""
    return render_template('about.html')


@app.route('/contact')
def contact_page():
    """Contact page"""
    return render_template('contact.html')


@app.route('/api/contact', methods=['POST'])
@csrf.exempt
def contact():
    """Handle contact form submissions"""
    form = ContactForm(data=request.get_json(), meta={'csrf': False})
    
    if form.validate():
        # Save to database
        contact_msg = Contact(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                subject=f"Contact Form: {form.subject.data or 'New Message'}",
                recipients=[app.config['MAIL_DEFAULT_SENDER']],
                reply_to=form.email.data
            )
            msg.body = f"""
New contact form submission:

Name: {form.name.data}
Email: {form.email.data}
Phone: {form.phone.data or 'Not provided'}

Message:
{form.message.data}
            """
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contacting us. We will respond shortly.'
        })
    
    return jsonify({
        'success': False,
        'errors': form.errors
    }), 400


@app.route('/api/booking', methods=['POST'])
@csrf.exempt
def booking():
    """Handle booking requests"""
    form = BookingForm(data=request.get_json(), meta={'csrf': False})
    
    if form.validate():
        # Get room and check availability
        room = Room.query.get(form.room_id.data)
        if not room or not room.is_available:
            return jsonify({
                'success': False,
                'message': 'Room not available'
            }), 400
        
        # Calculate total price
        days = (form.check_out.data - form.check_in.data).days
        total_price = days * room.price_per_night
        
        # Create booking (requires authentication)
        user_id = current_user.id if current_user.is_authenticated else None
        
        new_booking = Booking(
            user_id=user_id,
            room_id=form.room_id.data,
            guest_name=form.guest_name.data,
            guest_email=form.guest_email.data,
            guest_phone=form.guest_phone.data,
            check_in=form.check_in.data,
            check_out=form.check_out.data,
            num_guests=form.num_guests.data,
            total_price=total_price,
            special_requests=form.special_requests.data
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        # Send confirmation email
        try:
            msg = Message(
                subject=f"Booking Confirmation - {room.name}",
                recipients=[form.guest_email.data]
            )
            msg.body = f"""
Dear {form.guest_name.data},

Thank you for your booking request at Gancheng B&B!

Booking Details:
- Room: {room.name}
- Check-in: {form.check_in.data.strftime('%B %d, %Y')}
- Check-out: {form.check_out.data.strftime('%B %d, %Y')}
- Guests: {form.num_guests.data}
- Total: NT$ {total_price:,.0f}

Your booking is currently pending confirmation. We will contact you shortly to confirm availability.

Best regards,
Gancheng B&B Team
            """
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Booking request received. Check your email for confirmation.',
            'booking_id': new_booking.id
        })
    
    return jsonify({
        'success': False,
        'errors': form.errors
    }), 400


@app.route('/api/rooms')
def get_rooms():
    """API endpoint for room data"""
    rooms = Room.query.filter_by(is_available=True).all()
    
    # If database is empty, return default data
    if not rooms:
        return jsonify([
            {
                'id': 1,
                'name': 'Mountain View Suite',
                'type': 'Double',
                'description': 'Panoramic views of the Central Mountain Range with private balcony.',
                'amenities': ['wifi', 'ac_unit', 'bathtub'],
                'price_per_night': 3500,
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuAfSeuNAoDegBpufzWqzdrSSVT14xZxtfoHxcfSyc69724GJU9OoSIUQ9XtIdldIX6lt-3YYJnOEp2c-UWwoCtef72BPrWe9CoG54q8ytDqo194-mkyJhSaYvelJcHxAi0JfV7VblOgi0Ed7iSUs6kjNHJ8eUiDpwjQaTvwWEKdQJxHiVcY1uMXVAtLADX9Obg2YUvP16PD5qEF_0dU3dAREY5gZFoR_b5EKozOotoV4BnsLAlCZy5VFWhp8FBIWKn7wKZ3YJMzZZs'
            },
            {
                'id': 2,
                'name': 'Garden Room',
                'type': 'Queen',
                'description': 'Direct access to our lush private gardens, perfect for morning meditation.',
                'amenities': ['wifi', 'ac_unit', 'yard'],
                'price_per_night': 3000,
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuD3U8bU2YjeeHA7KtMjl87sGK3BQo3c4yxM1vmVBsjlk0E5hd1kaF_kUv3tZCMdjl19a1dHO9kjtyKwSVFfxjl7gQbbuuPLIhsyAvtx-frxaULsbn99DaMIdF3NfNNdZS7sbp5Mck6yZ2ov12BJNAxUmeSqNrBvmwWG2SBszwhMlvXq_cW6QA5lnuBhENmkm3EQw51eS0XalhXND33EldbotLjBmpPtCVjub5F12fAWtU8FJlGq1Vh-n9TqS2LD1DF68WqvddGCdHQ'
            },
            {
                'id': 3,
                'name': 'Family Villa',
                'type': 'Family',
                'description': 'Spacious accommodation for the whole family with separate living area.',
                'amenities': ['wifi', 'kitchen', 'tv'],
                'price_per_night': 5000,
                'image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuAc5I5gOEfXLGf85VNLedCV4wKwVtoL-tk7VCdHA4AcLKmHwT49rWefxSZvPhvAoObl2kBvADc_uXUD-FUsROyUmPviYgDmVbWfzV3NJ1ccsmf9sBHI5LF6VG6pcS6wkSSMnWyhmRn4_80IUyto-pBoQdwE7xXrkT6vPJ8bt1XSkXrV5InMpRT0Z0Ler-heyhUhHTgKk3zBI0-lSuedBU6Bl7G3gLuajY7xtavskWjFhPoWsMRDUtAMXsWxgbKtuVAlUOflDgCAYWI'
            }
        ])
    
    return jsonify([{
        'id': room.id,
        'name': room.name,
        'type': room.room_type,
        'description': room.description,
        'amenities': room.amenities.split(',') if room.amenities else [],
        'price_per_night': room.price_per_night,
        'image': room.image_url
    } for room in rooms])


# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if request.method == 'POST':
        if request.is_json:
            form = RegisterForm(data=request.get_json())
        
        if form.validate_on_submit():
            # Check if user already exists
            if User.query.filter_by(email=form.email.data).first():
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Email already registered'}), 400
                flash('Email already registered', 'error')
                return render_template('register.html', form=form)
            
            if User.query.filter_by(username=form.username.data).first():
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Username already taken'}), 400
                flash('Username already taken', 'error')
                return render_template('register.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Registration successful'})
            
            flash('Registration successful! Welcome to Gancheng B&B', 'success')
            return redirect(url_for('index'))
        
        if request.is_json:
            return jsonify({'success': False, 'errors': form.errors}), 400
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        if request.is_json:
            form = LoginForm(data=request.get_json())
        
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                
                if request.is_json:
                    return jsonify({'success': True, 'message': 'Login successful'})
                
                flash('Welcome back!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            
            flash('Invalid email or password', 'error')
        
        if request.is_json:
            return jsonify({'success': False, 'errors': form.errors}), 400
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    """User profile with bookings"""
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('profile.html', bookings=bookings)


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with full database access"""
    # Get all data from database
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    rooms = Room.query.all()
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Calculate statistics
    stats = {
        'total_bookings': Booking.query.count(),
        'pending_bookings': Booking.query.filter_by(status='pending').count(),
        'new_contacts': Contact.query.filter_by(status='new').count(),
        'total_users': User.query.count()
    }
    
    return render_template('admin.html', 
                         bookings=bookings, 
                         contacts=contacts, 
                         rooms=rooms, 
                         users=users,
                         stats=stats)


@app.route('/room/<int:room_id>')
def room_detail(room_id):
    """Room detail page"""
    room = Room.query.get_or_404(room_id)
    today = date.today().isoformat()
    return render_template('room_detail.html', room=room, today=today)


# Admin CRUD Routes
@app.route('/admin/booking/<int:booking_id>/status', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def update_booking_status(booking_id):
    """Update booking status"""
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json()
    booking.status = data.get('status', booking.status)
    db.session.commit()
    return jsonify({'success': True, 'status': booking.status})


@app.route('/admin/booking/<int:booking_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@admin_required
def delete_booking(booking_id):
    """Delete a booking"""
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/room', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def create_room():
    """Create a new room"""
    try:
        data = request.get_json()
        room = Room(
            name=data['name'],
            room_type=data['room_type'],
            description=data.get('description', ''),
            price_per_night=float(data['price_per_night']),
            max_guests=int(data['max_guests']),
            amenities=data.get('amenities', ''),
            image_url=data.get('image_url', ''),
            is_available=data.get('is_available', True),
            is_featured=data.get('is_featured', False)
        )
        db.session.add(room)
        db.session.commit()
        return jsonify({'success': True, 'room_id': room.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/admin/room/<int:room_id>', methods=['PUT'])
@csrf.exempt
@login_required
@admin_required
def update_room(room_id):
    """Update a room"""
    try:
        room = Room.query.get_or_404(room_id)
        data = request.get_json()
        
        room.name = data.get('name', room.name)
        room.room_type = data.get('room_type', room.room_type)
        room.description = data.get('description', room.description)
        room.price_per_night = float(data.get('price_per_night', room.price_per_night))
        room.max_guests = int(data.get('max_guests', room.max_guests))
        room.amenities = data.get('amenities', room.amenities)
        room.image_url = data.get('image_url', room.image_url)
        room.is_available = data.get('is_available', room.is_available)
        room.is_featured = data.get('is_featured', room.is_featured)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/admin/room/<int:room_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@admin_required
def delete_room(room_id):
    """Delete a room"""
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/contact/<int:contact_id>/status', methods=['POST'])
@csrf.exempt
@login_required
@admin_required
def update_contact_status(contact_id):
    """Update contact message status"""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    contact.status = data.get('status', contact.status)
    db.session.commit()
    return jsonify({'success': True, 'status': contact.status})


@app.route('/admin/contact/<int:contact_id>', methods=['DELETE'])
@csrf.exempt
@login_required
@admin_required
def delete_contact(contact_id):
    """Delete a contact message"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True})


# Database initialization
@app.before_request
def create_tables():
    """Create database tables before first request"""
    db.create_all()


@app.route('/init-db')
def init_database():
    """Initialize database - call this once after deployment"""
    try:
        # Create all tables
        db.create_all()
        
        # Check if already initialized
        if User.query.count() > 0:
            return jsonify({'message': 'Database already initialized'}), 200
        
        # Add sample rooms
        rooms = [
            Room(
                name='Mountain View Suite',
                room_type='Double',
                description='Panoramic views of the Central Mountain Range with private balcony.',
                image_url='https://lh3.googleusercontent.com/aida-public/AB6AXuAfSeuNAoDegBpufzWqzdrSSVT14xZxtfoHxcfSyc69724GJU9OoSIUQ9XtIdldIX6lt-3YYJnOEp2c-UWwoCtef72BPrWe9CoG54q8ytDqo194-mkyJhSaYvelJcHxAi0JfV7VblOgi0Ed7iSUs6kjNHJ8eUiDpwjQaTvwWEKdQJxHiVcY1uMXVAtLADX9Obg2YUvP16PD5qEF_0dU3dAREY5gZFoR_b5EKozOotoV4BnsLAlCZy5VFWhp8FBIWKn7wKZ3YJMzZZs',
                price_per_night=3500,
                max_guests=2,
                amenities='wifi,ac_unit,bathtub',
                is_available=True,
                is_featured=True
            ),
            Room(
                name='Garden Room',
                room_type='Queen',
                description='Direct access to our lush private gardens, perfect for morning meditation.',
                image_url='https://lh3.googleusercontent.com/aida-public/AB6AXuD3U8bU2YjeeHA7KtMjl87sGK3BQo3c4yxM1vmVBsjlk0E5hd1kaF_kUv3tZCMdjl19a1dHO9kjtyKwSVFfxjl7gQbbuuPLIhsyAvtx-frxaULsbn99DaMIdF3NfNNdZS7sbp5Mck6yZ2ov12BJNAxUmeSqNrBvmwWG2SBszwhMlvXq_cW6QA5lnuBhENmkm3EQw51eS0XalhXND33EldbotLjBmpPtCVjub5F12fAWtU8FJlGq1Vh-n9TqS2LD1DF68WqvddGCdHQ',
                price_per_night=3000,
                max_guests=2,
                amenities='wifi,ac_unit,yard',
                is_available=True,
                is_featured=True
            ),
            Room(
                name='Family Villa',
                room_type='Family',
                description='Spacious accommodation for the whole family with separate living area.',
                image_url='https://lh3.googleusercontent.com/aida-public/AB6AXuAc5I5gOEfXLGf85VNLedCV4wKwVtoL-tk7VCdHA4AcLKmHwT49rWefxSZvPhvAoObl2kBvADc_uXUD-FUsROyUmPviYgDmVbWfzV3NJ1ccsmf9sBHI5LF6VG6pcS6wkSSMnWyhmRn4_80IUyto-pBoQdwE7xXrkT6vPJ8bt1XSkXrV5InMpRT0Z0Ler-heyhUhHTgKk3zBI0-lSuedBU6Bl7G3gLuajY7xtavskWjFhPoWsMRDUtAMXsWxgbKtuVAlUOflDgCAYWI',
                price_per_night=5000,
                max_guests=5,
                amenities='wifi,kitchen,tv',
                is_available=True,
                is_featured=False
            )
        ]
        
        for room in rooms:
            db.session.add(room)
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@gangcheng.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Database initialized successfully',
            'rooms_added': len(rooms),
            'admin_created': True,
            'admin_email': 'admin@gangcheng.com',
            'admin_password': 'admin123 (please change after login)'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use Railway's PORT environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
