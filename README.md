# Football Fan App ⚽

A comprehensive football fan application featuring:

## Features

- 🌍 **All Major Leagues**: Browse leagues from around the world
- 💬 **Fan Opinions**: Leave comments and opinions on matches and teams
- 💭 **Live Chat**: Real-time chat with other football fans
- 🎥 **Match Highlights**: Watch highlights from previous games
- 📺 **Live Match Links**: Access links to live football streams
- 📊 **League Standings**: View current league tables
- 📅 **Match Schedules**: See upcoming and past fixtures

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Real-time**: Socket.IO for live chat
- **API**: Football-Data.org API for match data

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser to `http://localhost:5000`

## API Keys

- Get a free API key from [Football-Data.org](https://www.football-data.org/)
- Add it to your `.env` file

## Project Structure

```
football-fan-app/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # HTML templates
└── database/           # SQLite database
```

## License

MIT License
