from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from bson.objectid import ObjectId
import json
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Flask Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/garage_focus')

# File upload configuration
UPLOAD_FOLDER = 'static/assets/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'glb', 'gltf', 'fbx', 'obj'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Application configuration
APP_CONFIG = {
    'FLASK_HOST': os.environ.get('FLASK_HOST', '0.0.0.0'),
    'FLASK_PORT': int(os.environ.get('FLASK_PORT', 8000)),
    'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
    'MIN_FOCUS_DURATION': int(os.environ.get('MIN_FOCUS_DURATION', 5)),
    'TOTAL_MINUTES_FOR_100_PERCENT': int(os.environ.get('TOTAL_MINUTES_FOR_100_PERCENT', 300)),
    'SCRAP_METAL_PER_MINUTE': int(os.environ.get('SCRAP_METAL_PER_MINUTE', 1)),
    'GRACE_PERIOD': int(os.environ.get('GRACE_PERIOD', 10)),
    'ADMIN_USERNAME': os.environ.get('ADMIN_USERNAME', 'admin'),
    'ADMIN_PASSWORD': os.environ.get('ADMIN_PASSWORD', 'garage123'),
}

mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    return session.get('is_admin', False)

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

# ================== ADMIN DASHBOARD ROUTES ==================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == APP_CONFIG['ADMIN_USERNAME'] and password == APP_CONFIG['ADMIN_PASSWORD']:
            session['is_admin'] = True
            session['admin_user'] = username
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash('Admin logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    # Get statistics
    stats = {
        'total_users': mongo.db.users.count_documents({}),
        'total_cars': mongo.db.user_cars.count_documents({}),
        'completed_cars': mongo.db.user_cars.count_documents({'is_completed': True}),
        'car_templates': mongo.db.car_templates.count_documents({}),
        'total_focus_time': list(mongo.db.user_cars.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$total_focus_minutes'}}}
        ]))
    }
    
    if stats['total_focus_time']:
        stats['total_focus_hours'] = round(stats['total_focus_time'][0]['total'] / 60, 2)
    else:
        stats['total_focus_hours'] = 0
    
    # Get recent activity
    recent_users = list(mongo.db.users.find().sort('created_at', -1).limit(5))
    recent_cars = list(mongo.db.user_cars.find().sort('created_at', -1).limit(5))
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_cars=recent_cars)

@app.route('/admin/cars')
def admin_cars():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    car_templates = list(mongo.db.car_templates.find())
    return render_template('admin/cars.html', car_templates=car_templates)

@app.route('/admin/cars/new', methods=['GET', 'POST'])
def admin_new_car():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Handle form submission
        model_id = request.form['model_id']
        name = request.form['name']
        total_minutes = int(request.form['total_minutes'])
        
        # Check if model_id already exists
        if mongo.db.car_templates.find_one({'model_id': model_id}):
            flash('Model ID already exists', 'error')
            return render_template('admin/car_form.html')
        
        # Create new car template
        new_car = {
            'model_id': model_id,
            'name': name,
            'total_focus_minutes_required': total_minutes,
            'stages': [
                {"threshold": 0, "image_url": "", "model_3d_url": "", "description": "Rusted Junk"},
                {"threshold": 25, "image_url": "", "model_3d_url": "", "description": "Getting Started"},
                {"threshold": 50, "image_url": "", "model_3d_url": "", "description": "Half Restored"},
                {"threshold": 75, "image_url": "", "model_3d_url": "", "description": "Almost Done"},
                {"threshold": 100, "image_url": "", "model_3d_url": "", "description": "Showroom Ready"}
            ],
            'created_at': datetime.utcnow(),
            'created_by': session['admin_user']
        }
        
        result = mongo.db.car_templates.insert_one(new_car)
        flash(f'Car template "{name}" created successfully', 'success')
        return redirect(url_for('admin_edit_car', car_id=str(result.inserted_id)))
    
    return render_template('admin/car_form.html')

@app.route('/admin/cars/<car_id>/edit')
def admin_edit_car(car_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    car = mongo.db.car_templates.find_one({'_id': ObjectId(car_id)})
    if not car:
        flash('Car template not found', 'error')
        return redirect(url_for('admin_cars'))
    
    return render_template('admin/car_edit.html', car=car)

@app.route('/admin/cars/<car_id>/delete', methods=['POST'])
def admin_delete_car(car_id):
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    result = mongo.db.car_templates.delete_one({'_id': ObjectId(car_id)})
    if result.deleted_count > 0:
        flash('Car template deleted successfully', 'success')
    else:
        flash('Car template not found', 'error')
    
    return redirect(url_for('admin_cars'))

@app.route('/admin/upload', methods=['GET', 'POST'])
def admin_upload():
    if not is_admin():
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        asset_type = request.form.get('asset_type', '2d')  # '2d' or '3d'
        car_id = request.form.get('car_id')
        stage_threshold = request.form.get('stage_threshold', '0')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Create directory structure
            if asset_type == '3d':
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], '3d')
            else:
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], '2d')
            
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, unique_filename)
            
            try:
                file.save(file_path)
                
                # Update car template if specified
                if car_id and car_id != '':
                    stage_threshold = int(stage_threshold)
                    update_field = 'model_3d_url' if asset_type == '3d' else 'image_url'
                    file_url = f"/static/assets/uploads/{asset_type}/{unique_filename}"
                    
                    mongo.db.car_templates.update_one(
                        {
                            '_id': ObjectId(car_id),
                            'stages.threshold': stage_threshold
                        },
                        {
                            '$set': {f'stages.$.{update_field}': file_url}
                        }
                    )
                
                flash(f'File uploaded successfully: {unique_filename}', 'success')
                
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'error')
        else:
            flash('Invalid file type', 'error')
    
    # Get car templates for dropdown
    car_templates = list(mongo.db.car_templates.find())
    uploaded_files = []
    
    # Get existing uploaded files
    for asset_type in ['2d', '3d']:
        type_path = os.path.join(app.config['UPLOAD_FOLDER'], asset_type)
        if os.path.exists(type_path):
            files = os.listdir(type_path)
            for file in files:
                uploaded_files.append({
                    'filename': file,
                    'type': asset_type,
                    'url': f"/static/assets/uploads/{asset_type}/{file}",
                    'size': os.path.getsize(os.path.join(type_path, file))
                })
    
    return render_template('admin/upload.html', 
                         car_templates=car_templates,
                         uploaded_files=uploaded_files)

@app.route('/api/admin/update_car_stage', methods=['POST'])
def admin_update_car_stage():
    if not is_admin():
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    data = request.get_json()
    car_id = data.get('car_id')
    stage_threshold = int(data.get('stage_threshold'))
    updates = data.get('updates', {})
    
    try:
        # Update the specific stage
        for field, value in updates.items():
            mongo.db.car_templates.update_one(
                {
                    '_id': ObjectId(car_id),
                    'stages.threshold': stage_threshold
                },
                {
                    '$set': {f'stages.$.{field}': value}
                }
            )
        
        return jsonify({'success': True, 'message': 'Stage updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ================== 3D CAR VIEWER API ==================

@app.route('/api/car_3d/<model_id>')
def get_car_3d_model(model_id):
    """Get 3D model data for a specific car and progress"""
    progress = float(request.args.get('progress', 0))
    
    car_template = mongo.db.car_templates.find_one({'model_id': model_id})
    if not car_template:
        return jsonify({'error': 'Car template not found'}), 404
    
    # Find the appropriate stage based on progress
    current_stage = None
    for stage in car_template['stages']:
        if progress >= stage['threshold']:
            current_stage = stage
        else:
            break
    
    if not current_stage:
        current_stage = car_template['stages'][0]
    
    return jsonify({
        'model_3d_url': current_stage.get('model_3d_url', ''),
        'image_url': current_stage.get('image_url', ''),
        'description': current_stage.get('description', ''),
        'progress': progress,
        'stage_threshold': current_stage.get('threshold', 0)
    })

if __name__ == '__main__':
    with app.app_context():
        init_car_templates()
    app.run(
        debug=APP_CONFIG['FLASK_DEBUG'],
        host=APP_CONFIG['FLASK_HOST'],
        port=APP_CONFIG['FLASK_PORT']
    )
