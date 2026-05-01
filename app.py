from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///football_fans.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY', '')
FOOTBALL_API_BASE = 'https://api.football-data.org/v4'
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    favorite_team = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='opinions')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='messages')

class Highlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LiveStream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), nullable=False)
    stream_url = db.Column(db.String(500), nullable=False)
    platform = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FantasyLeague(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_teams = db.Column(db.Integer, default=10)
    budget = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    creator = db.relationship('User', backref='created_leagues')

class FantasyTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('fantasy_league.id'), nullable=False)
    total_points = db.Column(db.Integer, default=0)
    budget_remaining = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='fantasy_teams')
    league = db.relationship('FantasyLeague', backref='teams')

class FantasyPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('fantasy_team.id'), nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    player_team = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(20), nullable=False)  # GK, DEF, MID, FWD
    price = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    is_captain = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    team = db.relationship('FantasyTeam', backref='players')

# Helper function to call Football API
def call_football_api(endpoint):
    headers = {'X-Auth-Token': FOOTBALL_API_KEY}
    try:
        response = requests.get(f"{FOOTBALL_API_BASE}/{endpoint}", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

# Helper function to search YouTube for highlights
def search_youtube_highlights(query, max_results=3):
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == 'your_youtube_api_key_here':
        return []
    
    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': YOUTUBE_API_KEY,
            'order': 'relevance',
            'videoDuration': 'short'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            highlights = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                highlights.append({
                    'title': item['snippet']['title'],
                    'video_url': f'https://www.youtube.com/watch?v={video_id}',
                    'embed_url': f'https://www.youtube.com/embed/{video_id}',
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
                    'channel': item['snippet']['channelTitle']
                })
            return highlights
        return []
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return []

# Helper function to get popular football highlights
def get_popular_highlights():
    """Get popular football highlights from curated sources"""
    highlights = [
        {
            'title': 'Premier League Highlights',
            'video_url': 'https://www.youtube.com/c/premierleague',
            'thumbnail_url': 'https://crests.football-data.org/PL.png',
            'channel': 'Premier League Official'
        },
        {
            'title': 'Champions League Highlights',
            'video_url': 'https://www.youtube.com/c/championsleague',
            'thumbnail_url': 'https://crests.football-data.org/CL.png',
            'channel': 'UEFA Champions League'
        },
        {
            'title': 'La Liga Highlights',
            'video_url': 'https://www.youtube.com/c/laliga',
            'thumbnail_url': 'https://crests.football-data.org/PD.png',
            'channel': 'LaLiga Official'
        },
        {
            'title': 'Serie A Highlights',
            'video_url': 'https://www.youtube.com/c/seriea',
            'thumbnail_url': 'https://crests.football-data.org/SA.png',
            'channel': 'Serie A Official'
        },
        {
            'title': 'Bundesliga Highlights',
            'video_url': 'https://www.youtube.com/c/bundesliga',
            'thumbnail_url': 'https://crests.football-data.org/BL1.png',
            'channel': 'Bundesliga Official'
        }
    ]
    return highlights

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/leagues')
def leagues():
    # Get all available competitions
    competitions = call_football_api('competitions')
    return render_template('leagues.html', competitions=competitions)

@app.route('/league/<league_code>')
def league_detail(league_code):
    # Get league standings
    standings = call_football_api(f'competitions/{league_code}/standings')
    matches = call_football_api(f'competitions/{league_code}/matches')
    return render_template('league_detail.html', standings=standings, matches=matches, league_code=league_code)

@app.route('/match/<match_id>')
def match_detail(match_id):
    # Get match details
    match = call_football_api(f'matches/{match_id}')
    
    # Get opinions for this match
    opinions = Opinion.query.filter_by(match_id=match_id).order_by(Opinion.created_at.desc()).all()
    
    # Get highlights from database
    db_highlights = Highlight.query.filter_by(match_id=match_id).all()
    
    # Try to fetch YouTube highlights if match data is available
    youtube_highlights = []
    if match and match.get('match'):
        home_team = match['match']['homeTeam']['name']
        away_team = match['match']['awayTeam']['name']
        search_query = f"{home_team} vs {away_team} highlights"
        youtube_highlights = search_youtube_highlights(search_query, max_results=3)
    
    # Combine highlights
    all_highlights = list(db_highlights) + youtube_highlights
    
    # Get live streams
    streams = LiveStream.query.filter_by(match_id=match_id, is_active=True).all()
    
    return render_template('match_detail.html', match=match, opinions=opinions, 
                         highlights=all_highlights, streams=streams, match_id=match_id)

@app.route('/highlights')
def highlights():
    # Get popular highlights
    popular = get_popular_highlights()
    
    # Get recent highlights from database
    recent = Highlight.query.order_by(Highlight.created_at.desc()).limit(10).all()
    
    return render_template('highlights.html', popular=popular, recent=recent)

# World Cup Routes
@app.route('/worldcup')
def worldcup():
    # Get World Cup competition data
    worldcup_data = call_football_api('competitions/WC')
    matches = call_football_api('competitions/WC/matches')
    standings = call_football_api('competitions/WC/standings')
    
    return render_template('worldcup.html', 
                         worldcup=worldcup_data, 
                         matches=matches, 
                         standings=standings)

@app.route('/worldcup/match/<match_id>')
def worldcup_match(match_id):
    # Get match details
    match = call_football_api(f'matches/{match_id}')
    
    # Get opinions for this match
    opinions = Opinion.query.filter_by(match_id=match_id).order_by(Opinion.created_at.desc()).all()
    
    # Get highlights
    highlights = Highlight.query.filter_by(match_id=match_id).all()
    
    return render_template('worldcup_match.html', 
                         match=match, 
                         opinions=opinions, 
                         highlights=highlights,
                         match_id=match_id)

# Fantasy League Routes
@app.route('/fantasy')
def fantasy():
    return render_template('fantasy.html')

@app.route('/fantasy/create-league', methods=['GET', 'POST'])
def create_fantasy_league():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Generate unique code
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        league = FantasyLeague(
            name=data['name'],
            code=code,
            creator_id=session['user_id'],
            max_teams=data.get('max_teams', 10),
            budget=data.get('budget', 100)
        )
        
        db.session.add(league)
        db.session.commit()
        
        return jsonify({'success': True, 'league_id': league.id, 'code': code})
    
    return render_template('create_fantasy_league.html')

@app.route('/fantasy/join/<code>')
def join_fantasy_league(code):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    league = FantasyLeague.query.filter_by(code=code).first_or_404()
    
    # Check if user already has a team in this league
    existing_team = FantasyTeam.query.filter_by(
        user_id=session['user_id'],
        league_id=league.id
    ).first()
    
    if existing_team:
        return redirect(url_for('fantasy_team', team_id=existing_team.id))
    
    # Check if league is full
    if len(league.teams) >= league.max_teams:
        return render_template('error.html', message='League is full')
    
    return render_template('join_fantasy_league.html', league=league)

@app.route('/fantasy/create-team', methods=['POST'])
def create_fantasy_team():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    league = FantasyLeague.query.get_or_404(data['league_id'])
    
    team = FantasyTeam(
        name=data['team_name'],
        user_id=session['user_id'],
        league_id=league.id,
        budget_remaining=league.budget
    )
    
    db.session.add(team)
    db.session.commit()
    
    return jsonify({'success': True, 'team_id': team.id})

@app.route('/fantasy/team/<int:team_id>')
def fantasy_team(team_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    team = FantasyTeam.query.get_or_404(team_id)
    
    # Check if user owns this team
    if team.user_id != session['user_id']:
        return render_template('error.html', message='Access denied')
    
    # Get players grouped by position
    players = {
        'GK': FantasyPlayer.query.filter_by(team_id=team_id, position='GK').all(),
        'DEF': FantasyPlayer.query.filter_by(team_id=team_id, position='DEF').all(),
        'MID': FantasyPlayer.query.filter_by(team_id=team_id, position='MID').all(),
        'FWD': FantasyPlayer.query.filter_by(team_id=team_id, position='FWD').all()
    }
    
    return render_template('fantasy_team.html', team=team, players=players)

@app.route('/fantasy/league/<int:league_id>')
def fantasy_league_detail(league_id):
    league = FantasyLeague.query.get_or_404(league_id)
    
    # Get teams sorted by points
    teams = FantasyTeam.query.filter_by(league_id=league_id).order_by(FantasyTeam.total_points.desc()).all()
    
    return render_template('fantasy_league_detail.html', league=league, teams=teams)

@app.route('/fantasy/add-player', methods=['POST'])
def add_fantasy_player():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    team = FantasyTeam.query.get_or_404(data['team_id'])
    
    # Check ownership
    if team.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check budget
    if team.budget_remaining < data['price']:
        return jsonify({'error': 'Insufficient budget'}), 400
    
    # Check position limits
    position_count = FantasyPlayer.query.filter_by(team_id=team.id, position=data['position']).count()
    limits = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
    
    if position_count >= limits.get(data['position'], 0):
        return jsonify({'error': f'Maximum {limits.get(data["position"])} {data["position"]} players allowed'}), 400
    
    player = FantasyPlayer(
        team_id=team.id,
        player_name=data['player_name'],
        player_team=data['player_team'],
        position=data['position'],
        price=data['price']
    )
    
    team.budget_remaining -= data['price']
    
    db.session.add(player)
    db.session.commit()
    
    return jsonify({'success': True, 'player_id': player.id, 'budget_remaining': team.budget_remaining})

@app.route('/fantasy/remove-player/<int:player_id>', methods=['POST'])
def remove_fantasy_player(player_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    player = FantasyPlayer.query.get_or_404(player_id)
    team = player.team
    
    # Check ownership
    if team.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    team.budget_remaining += player.price
    
    db.session.delete(player)
    db.session.commit()
    
    return jsonify({'success': True, 'budget_remaining': team.budget_remaining})

@app.route('/fantasy/set-captain/<int:player_id>', methods=['POST'])
def set_captain(player_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    player = FantasyPlayer.query.get_or_404(player_id)
    team = player.team
    
    # Check ownership
    if team.user_id != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Remove captain from all players
    FantasyPlayer.query.filter_by(team_id=team.id).update({'is_captain': False})
    
    # Set new captain
    player.is_captain = True
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/chat/<room>')
def chat_room(room):
    return render_template('chat_room.html', room=room)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(username=data['username'], email=data['email'], 
                   favorite_team=data.get('favorite_team', ''))
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/opinion', methods=['POST'])
def post_opinion():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    opinion = Opinion(
        user_id=session['user_id'],
        match_id=data['match_id'],
        content=data['content']
    )
    
    db.session.add(opinion)
    db.session.commit()
    
    return jsonify({'success': True, 'opinion_id': opinion.id})

@app.route('/api/opinion/<int:opinion_id>/like', methods=['POST'])
def like_opinion(opinion_id):
    opinion = Opinion.query.get_or_404(opinion_id)
    opinion.likes += 1
    db.session.commit()
    return jsonify({'success': True, 'likes': opinion.likes})

# Socket.IO Events for Real-time Chat
@socketio.on('join')
def on_join(data):
    username = session.get('username', 'Anonymous')
    room = data['room']
    join_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = session.get('username', 'Anonymous')
    room = data['room']
    leave_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has left the room.'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    username = session.get('username', 'Anonymous')
    room = data['room']
    message = data['message']
    
    # Save to database if user is logged in
    if 'user_id' in session:
        chat_msg = ChatMessage(
            user_id=session['user_id'],
            room=room,
            message=message
        )
        db.session.add(chat_msg)
        db.session.commit()
    
    emit('message', {
        'username': username,
        'message': message,
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }, room=room)

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
