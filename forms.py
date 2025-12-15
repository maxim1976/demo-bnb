from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from datetime import date


class ContactForm(FlaskForm):
    """Contact form with validation"""
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    phone = StringField('Phone', validators=[
        Length(max=20, message='Phone number too long')
    ])
    subject = StringField('Subject', validators=[
        Length(max=200, message='Subject too long')
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=10, max=2000, message='Message must be between 10 and 2000 characters')
    ])


class BookingForm(FlaskForm):
    """Booking request form with validation"""
    room_id = IntegerField('Room', validators=[
        DataRequired(message='Please select a room')
    ])
    guest_name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100)
    ])
    guest_email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    guest_phone = StringField('Phone', validators=[
        DataRequired(message='Phone is required'),
        Length(min=8, max=20)
    ])
    check_in = DateField('Check-in Date', validators=[
        DataRequired(message='Check-in date is required')
    ])
    check_out = DateField('Check-out Date', validators=[
        DataRequired(message='Check-out date is required')
    ])
    num_guests = IntegerField('Number of Guests', validators=[
        DataRequired(message='Number of guests is required'),
        NumberRange(min=1, max=10, message='Number of guests must be between 1 and 10')
    ])
    special_requests = TextAreaField('Special Requests', validators=[
        Length(max=500, message='Special requests too long')
    ])
    
    def validate_check_out(self, field):
        """Ensure check-out is after check-in"""
        if self.check_in.data and field.data:
            if field.data <= self.check_in.data:
                raise ValidationError('Check-out date must be after check-in date')
    
    def validate_check_in(self, field):
        """Ensure check-in is not in the past"""
        if field.data and field.data < date.today():
            raise ValidationError('Check-in date cannot be in the past')


class LoginForm(FlaskForm):
    """User login form"""
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])


class RegisterForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
