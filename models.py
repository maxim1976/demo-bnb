from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Room(db.Model):
    """Room model for accommodations"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # Double, Queen, Family
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    price_per_night = db.Column(db.Float, nullable=False)
    max_guests = db.Column(db.Integer, default=2)
    amenities = db.Column(db.String(500))  # Comma-separated: wifi,ac_unit,bathtub
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # Show on homepage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='room', lazy=True)
    
    def to_dict(self):
        """Convert room to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'room_type': self.room_type,
            'description': self.description,
            'image_url': self.image_url or '',
            'price_per_night': self.price_per_night,
            'max_guests': self.max_guests,
            'amenities': self.amenities or '',
            'is_available': self.is_available,
            'is_featured': self.is_featured
        }
    
    def __repr__(self):
        return f'<Room {self.name}>'


class Booking(db.Model):
    """Booking model for reservations"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allow guest bookings
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    
    # Guest information
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20))
    
    # Booking details
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    num_guests = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Status: pending, confirmed, cancelled, completed
    status = db.Column(db.String(20), default='pending')
    special_requests = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.guest_name}>'


class Contact(db.Model):
    """Contact form submissions"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    
    # Status: new, read, replied
    status = db.Column(db.String(20), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name} - {self.email}>'
