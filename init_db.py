"""Initialize database with sample data"""
from app import app, db
from models import Room, User

def init_db():
    """Create tables and add sample rooms"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if rooms already exist
        if Room.query.count() > 0:
            print("Database already initialized!")
            return
        
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
        admin.set_password('admin123')  # Change this!
        db.session.add(admin)
        
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print(f"   - Added {len(rooms)} rooms")
        print("   - Created admin user (admin@gangcheng.com / admin123)")
        print("\n⚠️  Remember to change the admin password!")


if __name__ == '__main__':
    init_db()
