import os
from app import app, db

def init_database():
    """Initialize the database with tables"""
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")
        print("Tables created:")
        print("- User")
        print("- Opinion")
        print("- ChatMessage")
        print("- Highlight")
        print("- LiveStream")

if __name__ == '__main__':
    init_database()
