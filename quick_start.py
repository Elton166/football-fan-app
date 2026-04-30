#!/usr/bin/env python3
"""
Quick Start Script for Football Fan App
This script helps you set up the application quickly
"""

import os
import sys
import secrets
import subprocess

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print("Please upgrade Python and try again")
        return False
    
    print("✅ Python version is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    print("Installing packages from requirements.txt...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Error installing dependencies")
        print("Please run manually: pip install -r requirements.txt")
        return False

def create_env_file():
    """Create .env file with configuration"""
    print_header("Creating Environment Configuration")
    
    if os.path.exists('.env'):
        overwrite = input(".env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            return True
    
    print("\nLet's set up your environment variables...")
    
    # Get API key
    print("\n📝 Football API Key:")
    print("Get your free API key from: https://www.football-data.org/")
    api_key = input("Enter your Football-Data.org API key (or press Enter to skip): ").strip()
    
    if not api_key:
        api_key = "your_api_key_here"
        print("⚠️  Warning: You'll need to add your API key later in the .env file")
    
    # Generate secret key
    secret_key = secrets.token_hex(32)
    
    # Create .env file
    env_content = f"""# Football Data API Key (get from https://www.football-data.org/)
FOOTBALL_API_KEY={api_key}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///database/football_fans.db
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully")
    print(f"   - Secret key generated: {secret_key[:20]}...")
    print(f"   - API key: {'Set' if api_key != 'your_api_key_here' else 'Not set (add later)'}")
    
    return True

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    # Create database directory
    os.makedirs('database', exist_ok=True)
    
    try:
        # Import and initialize
        from app import app, db
        
        with app.app_context():
            db.create_all()
        
        print("✅ Database initialized successfully")
        print("   Tables created:")
        print("   - User")
        print("   - Opinion")
        print("   - ChatMessage")
        print("   - Highlight")
        print("   - LiveStream")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_sample_user():
    """Optionally create a sample user"""
    print_header("Create Sample User (Optional)")
    
    create = input("Would you like to create a test user? (y/n): ").lower()
    
    if create != 'y':
        print("Skipping user creation")
        return True
    
    try:
        from app import app, db, User
        
        username = input("Username (default: testuser): ").strip() or "testuser"
        email = input("Email (default: test@example.com): ").strip() or "test@example.com"
        password = input("Password (default: password123): ").strip() or "password123"
        favorite_team = input("Favorite team (optional): ").strip()
        
        with app.app_context():
            # Check if user exists
            existing = User.query.filter_by(username=username).first()
            if existing:
                print(f"⚠️  User '{username}' already exists")
                return True
            
            user = User(
                username=username,
                email=email,
                favorite_team=favorite_team
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
        
        print(f"\n✅ User created successfully")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print_header("Setup Complete! 🎉")
    
    print("Your Football Fan App is ready to run!\n")
    print("Next steps:")
    print("\n1. Start the application:")
    print("   python app.py")
    print("\n2. Open your browser to:")
    print("   http://localhost:5000")
    print("\n3. If you haven't added your API key yet:")
    print("   - Edit the .env file")
    print("   - Add your Football-Data.org API key")
    print("   - Get one free at: https://www.football-data.org/")
    print("\n4. Explore the features:")
    print("   - Browse leagues and standings")
    print("   - Register an account")
    print("   - Join chat rooms")
    print("   - Share opinions on matches")
    print("\n📚 For more information, see:")
    print("   - README.md - Project overview")
    print("   - SETUP_GUIDE.md - Detailed setup instructions")
    print("   - FEATURES.md - Complete feature documentation")
    print("\n⚽ Enjoy your Football Fan App!")

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  ⚽ Football Fan App - Quick Start Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    install = input("\nInstall dependencies? (y/n): ").lower()
    if install == 'y':
        if not install_dependencies():
            print("\n⚠️  Continuing with setup, but you may need to install dependencies manually")
    
    # Create .env file
    if not create_env_file():
        print("\n⚠️  Warning: Environment configuration may be incomplete")
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Setup failed at database initialization")
        sys.exit(1)
    
    # Create sample user
    create_sample_user()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
