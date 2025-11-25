from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from bson.objectid import ObjectId
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Flask Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/garage_focus')

# Application configuration
APP_CONFIG = {
    'FLASK_HOST': os.environ.get('FLASK_HOST', '0.0.0.0'),
    'FLASK_PORT': int(os.environ.get('FLASK_PORT', 8000)),
    'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    'MIN_FOCUS_DURATION': int(os.environ.get('MIN_FOCUS_DURATION', 5)),
    'TOTAL_MINUTES_FOR_100_PERCENT': int(os.environ.get('TOTAL_MINUTES_FOR_100_PERCENT', 300)),
    'SCRAP_METAL_PER_MINUTE': int(os.environ.get('SCRAP_METAL_PER_MINUTE', 1)),
    'GRACE_PERIOD': int(os.environ.get('GRACE_PERIOD', 10)),
}

mongo = PyMongo(app)

# Initialize car templates data
def init_car_templates():
    """Initialize the car templates collection with default data"""
    if mongo.db.car_templates.count_documents({}) == 0:
        templates = [
            {
                "model_id": "mustang_1969",
                "name": "The Stallion",
                "total_focus_minutes_required": 300,
                "stages": [
                    {"threshold": 0, "image_url": "/static/assets/cars/mustang/stage0.png", "description": "Rusted Junk"},
                    {"threshold": 25, "image_url": "/static/assets/cars/mustang/stage1.png", "description": "Getting Started"},
                    {"threshold": 50, "image_url": "/static/assets/cars/mustang/stage2.png", "description": "Half Restored"},
                    {"threshold": 75, "image_url": "/static/assets/cars/mustang/stage3.png", "description": "Almost Done"},
                    {"threshold": 100, "image_url": "/static/assets/cars/mustang/stage4.png", "description": "Showroom Ready"}
                ]
            },
            {
                "model_id": "corvette_1965",
                "name": "The Stingray",
                "total_focus_minutes_required": 400,
                "stages": [
                    {"threshold": 0, "image_url": "/static/assets/cars/corvette/stage0.png", "description": "Rusted Junk"},
                    {"threshold": 25, "image_url": "/static/assets/cars/corvette/stage1.png", "description": "Getting Started"},
                    {"threshold": 50, "image_url": "/static/assets/cars/corvette/stage2.png", "description": "Half Restored"},
                    {"threshold": 75, "image_url": "/static/assets/cars/corvette/stage3.png", "description": "Almost Done"},
                    {"threshold": 100, "image_url": "/static/assets/cars/corvette/stage4.png", "description": "Showroom Ready"}
                ]
            }
        ]
        mongo.db.car_templates.insert_many(templates)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return redirect(url_for('login'))
    
    # Get current car
    current_car = None
    if user.get('current_car_id'):
        current_car = mongo.db.user_cars.find_one({'_id': ObjectId(user['current_car_id'])})
        if current_car:
            car_template = mongo.db.car_templates.find_one({'model_id': current_car['car_model']})
            current_car['template'] = car_template
    
    # Get completed cars for showroom
    completed_cars = list(mongo.db.user_cars.find({
        'user_id': session['user_id'], 
        'is_completed': True
    }))
    
    return render_template('garage.html', 
                         user=user, 
                         current_car=current_car, 
                         completed_cars=completed_cars)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if mongo.db.users.find_one({'username': username}):
            return render_template('register.html', error='Username already exists')
        
        # Create new user
        user_id = mongo.db.users.insert_one({
            'username': username,
            'password': generate_password_hash(password),
            'scrap_metal': 0,
            'blueprints': 0,
            'current_car_id': None,
            'created_at': datetime.utcnow()
        }).inserted_id
        
        session['user_id'] = str(user_id)
        return redirect(url_for('junkyard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/junkyard')
def junkyard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get available car templates
    car_templates = list(mongo.db.car_templates.find({}))
    return render_template('junkyard.html', car_templates=car_templates)

@app.route('/api/select_car', methods=['POST'])
def select_car():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    data = request.get_json()
    car_model = data.get('car_model')
    
    # Create new car instance for user
    car_id = mongo.db.user_cars.insert_one({
        'user_id': session['user_id'],
        'car_model': car_model,
        'restoration_progress': 0,
        'total_focus_minutes': 0,
        'parts_installed': {},
        'is_completed': False,
        'created_at': datetime.utcnow()
    }).inserted_id
    
    # Update user's current car
    mongo.db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'current_car_id': str(car_id)}}
    )
    
    return jsonify({'success': True, 'car_id': str(car_id)})

@app.route('/api/start_session', methods=['POST'])
def start_session():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    data = request.get_json()
    duration_minutes = int(data.get('duration', 25))
    task_description = data.get('task', 'Focus Session')
    
    # Store session data in user session
    session['active_session'] = {
        'start_time': datetime.utcnow().isoformat(),
        'duration_minutes': duration_minutes,
        'task_description': task_description,
        'user_id': session['user_id']
    }
    
    return jsonify({'success': True, 'session_id': session['user_id']})

@app.route('/api/complete_session', methods=['POST'])
def complete_session():
    if 'user_id' not in session or 'active_session' not in session:
        return jsonify({'success': False, 'error': 'No active session'})
    
    data = request.get_json()
    minutes_focused = float(data.get('minutes_focused', 0))
    was_successful = data.get('success', False)
    
    if not was_successful or minutes_focused < 5:  # Minimum 5 minutes for progress
        session.pop('active_session', None)
        return jsonify({'success': False, 'message': 'Session failed - dropped the wrench!'})
    
    # Get user and current car
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if not user or not user.get('current_car_id'):
        return jsonify({'success': False, 'error': 'No current car'})
    
    current_car = mongo.db.user_cars.find_one({'_id': ObjectId(user['current_car_id'])})
    if not current_car:
        return jsonify({'success': False, 'error': 'Car not found'})
    
    # Calculate progress and rewards
    scrap_metal_earned = int(minutes_focused)  # 1 minute = 1 scrap metal
    progress_increase = (minutes_focused / 300) * 100  # 300 minutes = 100%
    
    new_progress = min(100, current_car['restoration_progress'] + progress_increase)
    new_total_minutes = current_car['total_focus_minutes'] + minutes_focused
    
    # Update car progress
    updates = {
        'restoration_progress': new_progress,
        'total_focus_minutes': new_total_minutes,
        'last_session': datetime.utcnow()
    }
    
    # Check if car is completed
    if new_progress >= 100:
        updates['is_completed'] = True
        updates['completed_at'] = datetime.utcnow()
        
        # Clear user's current car so they can pick a new one
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$unset': {'current_car_id': ''}}
        )
    
    # Update car
    mongo.db.user_cars.update_one(
        {'_id': ObjectId(user['current_car_id'])},
        {'$set': updates}
    )
    
    # Update user's currency
    mongo.db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$inc': {'scrap_metal': scrap_metal_earned}}
    )
    
    # Clear session
    session.pop('active_session', None)
    
    return jsonify({
        'success': True,
        'progress': new_progress,
        'scrap_metal_earned': scrap_metal_earned,
        'car_completed': new_progress >= 100,
        'message': f'Great work! Earned {scrap_metal_earned} scrap metal!'
    })

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Keep session alive and detect if user is still active"""
    if 'user_id' not in session or 'active_session' not in session:
        return jsonify({'success': False, 'error': 'No active session'})
    
    return jsonify({'success': True, 'message': 'Session active'})

if __name__ == '__main__':
    with app.app_context():
        init_car_templates()
    app.run(
        debug=APP_CONFIG['FLASK_DEBUG'],
        host=APP_CONFIG['FLASK_HOST'],
        port=APP_CONFIG['FLASK_PORT']
    )
