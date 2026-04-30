# Football Fan App - Complete Setup Guide

## Prerequisites

Before you begin, make sure you have:
- Python 3.8 or higher installed
- pip (Python package manager)
- A web browser

## Step-by-Step Installation

### 1. Install Python (if not already installed)

**Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- Run the installer and **check "Add Python to PATH"**
- Verify installation:
  ```bash
  python --version
  ```

### 2. Install Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-SocketIO (real-time chat)
- Flask-SQLAlchemy (database)
- requests (API calls)
- python-dotenv (environment variables)

### 3. Get Your Football API Key

1. Visit [Football-Data.org](https://www.football-data.org/)
2. Click "Register" and create a free account
3. After registration, you'll receive an API key
4. The free tier includes:
   - 10 requests per minute
   - Access to major European leagues
   - Match data, standings, and fixtures

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor and add your API key:
   ```
   FOOTBALL_API_KEY=your_actual_api_key_here
   SECRET_KEY=your_random_secret_key_here
   ```

3. Generate a secure secret key (optional but recommended):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### 5. Initialize the Database

Run the database initialization script:

```bash
python init_db.py
```

You should see:
```
Database initialized successfully!
Tables created:
- User
- Opinion
- ChatMessage
- Highlight
- LiveStream
```

### 6. Run the Application

Start the Flask server:

```bash
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Restarting with stat
```

### 7. Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Features Overview

### 🌍 Browse Leagues
- Navigate to "Leagues" to see all available competitions
- Click on any league to view standings and fixtures

### 👤 User Registration
1. Click "Register" in the navigation
2. Create an account with username, email, and password
3. Optionally add your favorite team

### 💬 Post Opinions
1. Login to your account
2. Navigate to any match detail page
3. Share your thoughts in the opinion section
4. Like other fans' opinions

### 💭 Live Chat
1. Go to "Chat" section
2. Choose a chat room (General, Premier League, La Liga, etc.)
3. Chat in real-time with other football fans
4. Messages are saved to the database

### 🎥 Highlights & Streams
- Match detail pages show available highlights
- Live stream links are displayed for ongoing matches
- (Note: You'll need to add these manually via the database or admin panel)

## Adding Sample Data

### Add Highlights (Optional)

You can add highlights manually through Python:

```python
from app import app, db, Highlight

with app.app_context():
    highlight = Highlight(
        match_id="12345",
        title="Amazing Goal Compilation",
        video_url="https://youtube.com/watch?v=example",
        thumbnail_url="https://example.com/thumb.jpg"
    )
    db.session.add(highlight)
    db.session.commit()
```

### Add Live Streams (Optional)

```python
from app import app, db, LiveStream

with app.app_context():
    stream = LiveStream(
        match_id="12345",
        stream_url="https://example.com/stream",
        platform="YouTube",
        is_active=True
    )
    db.session.add(stream)
    db.session.commit()
```

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: API returns no data
**Solution:** 
- Check your API key in `.env` file
- Verify your API key is active on Football-Data.org
- Check if you've exceeded the rate limit (10 requests/minute on free tier)

### Issue: Database errors
**Solution:** Delete the database and reinitialize:
```bash
rm -rf database/
python init_db.py
```

### Issue: Port 5000 already in use
**Solution:** Change the port in `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Issue: Chat not working
**Solution:** 
- Make sure Socket.IO is properly installed
- Check browser console for errors
- Try refreshing the page

## Available League Codes

Common league codes for the API:
- `PL` - Premier League (England)
- `PD` - La Liga (Spain)
- `SA` - Serie A (Italy)
- `BL1` - Bundesliga (Germany)
- `FL1` - Ligue 1 (France)
- `CL` - Champions League
- `ELC` - Championship (England)
- `PPL` - Primeira Liga (Portugal)
- `DED` - Eredivisie (Netherlands)

## Upgrading to Production

For production deployment:

1. **Use PostgreSQL instead of SQLite:**
   ```
   DATABASE_URL=postgresql://user:password@localhost/football_fans
   ```

2. **Set DEBUG to False in app.py:**
   ```python
   socketio.run(app, debug=False, host='0.0.0.0', port=5000)
   ```

3. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn --worker-class eventlet -w 1 app:app
   ```

4. **Set strong SECRET_KEY**

5. **Use environment variables for sensitive data**

## Next Steps

- Customize the styling in `static/css/style.css`
- Add more chat rooms in `templates/chat.html`
- Integrate video APIs for automatic highlights
- Add user profiles and favorite teams
- Implement match predictions and polls
- Add push notifications for live matches

## Support

For issues or questions:
- Check the [Football-Data.org API documentation](https://www.football-data.org/documentation/quickstart)
- Review Flask documentation at [flask.palletsprojects.com](https://flask.palletsprojects.com/)

## License

MIT License - Feel free to modify and use for your own projects!

---

**Enjoy your Football Fan App! ⚽**
