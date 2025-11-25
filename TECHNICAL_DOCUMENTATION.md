# 🔧 Garage Focus - Technical Documentation

## Architecture Overview

Garage Focus is a full-stack web application built with Flask (Python) backend and vanilla JavaScript frontend. It uses MongoDB for data persistence and implements the Page Visibility API for focus detection.

### Tech Stack
- **Backend**: Python Flask with Flask-PyMongo
- **Database**: MongoDB (local or Atlas)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **PWA**: Service Worker ready, installable
- **APIs**: RESTful API endpoints, Page Visibility API

---

## Database Schema

### Collections

#### 1. `users`
```json
{
  "_id": ObjectId,
  "username": String (unique),
  "password": String (hashed),
  "scrap_metal": Number (currency),
  "blueprints": Number (future feature),
  "current_car_id": String (reference to user_cars),
  "created_at": DateTime
}
```

#### 2. `user_cars`
```json
{
  "_id": ObjectId,
  "user_id": String (reference to users),
  "car_model": String (mustang_1969, corvette_1965),
  "restoration_progress": Number (0-100),
  "total_focus_minutes": Number,
  "parts_installed": Object (future feature),
  "is_completed": Boolean,
  "created_at": DateTime,
  "completed_at": DateTime (optional),
  "last_session": DateTime (optional)
}
```

#### 3. `car_templates`
```json
{
  "_id": ObjectId,
  "model_id": String (unique),
  "name": String,
  "total_focus_minutes_required": Number,
  "stages": [
    {
      "threshold": Number (0-100),
      "image_url": String,
      "model_3d_url": String,
      "description": String
    }
  ],
  "created_at": DateTime,
  "created_by": String (admin_username)
}
```

#### 4. `uploaded_assets` (Implicit - Files on disk)
Asset files are stored in the filesystem at:
- `static/assets/uploads/2d/` - 2D images (PNG, JPG, GIF)
- `static/assets/uploads/3d/` - 3D models (GLB, GLTF, FBX, OBJ)

File naming convention: `{uuid}_{original_name}.{extension}`

---

## API Endpoints & User Flow

### Authentication Flow

#### 1. User Registration
**Frontend Action**: User fills registration form and clicks "GET GARAGE LICENSE"
**API Call**: `POST /register`
**Payload**:
```json
{
  "username": "string",
  "password": "string",
  "confirm_password": "string"
}
```
**Backend Logic**:
- Validates passwords match
- Checks username uniqueness
- Creates hashed password
- Creates new user document
- Sets session cookie
- Redirects to junkyard

#### 2. User Login
**Frontend Action**: User fills login form and clicks "START ENGINE"
**API Call**: `POST /login`
**Payload**: Form data (username, password)
**Backend Logic**:
- Validates credentials
- Sets session cookie
- Redirects to garage

#### 3. Logout
**Frontend Action**: User clicks "Logout"
**API Call**: `GET /logout`
**Backend Logic**:
- Clears session cookie
- Redirects to login

---

### Car Selection Flow

#### 4. View Junkyard
**Frontend Action**: User navigates to junkyard or clicks "Visit Junkyard"
**API Call**: `GET /junkyard`
**Backend Logic**:
- Fetches all car templates
- Renders junkyard with available cars

#### 5. Select Car
**Frontend Action**: User clicks "SELECT" button on a car
**API Call**: `POST /api/select_car`
**Payload**:
```json
{
  "car_model": "mustang_1969"
}
```
**Backend Logic**:
- Creates new user_car document
- Sets restoration_progress to 0
- Updates user's current_car_id
- Returns success response

**JavaScript Flow**:
```javascript
// 1. Show confirmation modal
confirmModal.classList.remove('hidden');

// 2. User confirms selection
fetch('/api/select_car', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ car_model: selectedCarModel })
})

// 3. Redirect to garage on success
window.location.href = '/';
```

---

### Focus Session Flow

#### 6. Start Focus Session
**Frontend Action**: User fills task input, selects duration, clicks "START ENGINE"
**API Call**: `POST /api/start_session`
**Payload**:
```json
{
  "duration": 25,
  "task": "Study calculus"
}
```
**Backend Logic**:
- Stores session data in server session
- Returns success response

**JavaScript Flow**:
```javascript
// 1. Validate input
if (!task) {
  alert('Please enter what you\'re working on!');
  return;
}

// 2. Start session
window.focusTimer.startSession(task, duration);

// 3. Show focus overlay
document.getElementById('focus-overlay').classList.remove('hidden');

// 4. Start timer and visibility monitoring
this.timerInterval = setInterval(() => this.updateTimerDisplay(), 1000);
this.heartbeatInterval = setInterval(() => this.sendHeartbeat(), 60000);
```

#### 7. Session Heartbeat
**Frontend Action**: Automatic every 60 seconds during active session
**API Call**: `POST /api/heartbeat`
**Payload**: Empty
**Backend Logic**:
- Validates active session exists
- Returns session status

#### 8. Tab Switch Detection
**Frontend Action**: User switches browser tab
**JavaScript Logic**:
```javascript
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === 'hidden') {
    this.handleTabSwitch(); // Start 10-second countdown
  } else {
    this.handleTabReturn(); // Check if return is within grace period
  }
});
```
**No API Call**: Handled entirely on frontend

#### 9. Complete Focus Session
**Frontend Action**: Session timer completes or user stops session
**API Call**: `POST /api/complete_session`
**Payload**:
```json
{
  "minutes_focused": 25.5,
  "success": true
}
```
**Backend Logic**:
- Validates active session
- Calculates progress: `(minutes_focused / 300) * 100`
- Calculates rewards: `scrap_metal = minutes_focused`
- Updates car restoration progress
- Updates user's scrap metal
- Checks if car is completed (progress >= 100)
- Clears user's current_car_id if completed
- Returns progress and rewards

**Success Response**:
```json
{
  "success": true,
  "progress": 15.5,
  "scrap_metal_earned": 25,
  "car_completed": false,
  "message": "Great work! Earned 25 scrap metal!"
}
```

---

### Navigation Flow

#### 10. View Garage (Home)
**Frontend Action**: User navigates to home page
**API Call**: `GET /`
**Backend Logic**:
- Fetches user data
- Fetches current car (if exists)
- Fetches car template for current car
- Fetches completed cars for showroom
- Renders garage view

---

## Frontend JavaScript Classes

### FocusTimer Class
Located in `templates/base.html`

**Key Methods**:
- `startSession(taskName, durationMinutes)`: Initializes focus session
- `updateTimerDisplay()`: Updates countdown timer every second
- `handleTabSwitch()`: Triggers warning when user leaves tab
- `handleTabReturn()`: Validates return within grace period
- `sendHeartbeat()`: Keeps session alive
- `stopSession(success)`: Ends session and sends completion data

**Key Properties**:
- `isActive`: Session state flag
- `startTime`: Session start timestamp
- `duration`: Session duration in minutes
- `tabSwitchTime`: Timestamp when user left tab

---

## Page Visibility API Implementation

The application uses the Page Visibility API to detect when users switch tabs:

```javascript
document.addEventListener("visibilitychange", () => {
  if (this.isActive) {
    if (document.visibilityState === 'hidden') {
      this.handleTabSwitch(); // Start grace period
    } else if (document.visibilityState === 'visible') {
      this.handleTabReturn(); // Check if within grace period
    }
  }
});
```

**Grace Period Logic**:
1. User switches tab → Start 10-second countdown
2. Show warning message with countdown
3. If user returns within 10 seconds → Continue session
4. If user doesn't return → Fail session automatically

---

## Progress Calculation

### Car Restoration Progress
- **Total Time Required**: 300 minutes (5 hours) for 100% completion
- **Progress Formula**: `(minutes_focused / 300) * 100`
- **Visual Stages**: 0%, 25%, 50%, 75%, 100%

### Reward System
- **Scrap Metal**: 1 scrap metal per minute focused
- **Minimum Session**: 5 minutes for any progress
- **Failed Session**: 0 rewards, no progress

---

## Session Management

### Server-Side Sessions
Flask sessions store:
- `user_id`: Current authenticated user
- `active_session`: Current focus session data

### Active Session Structure
```python
session['active_session'] = {
    'start_time': datetime.utcnow().isoformat(),
    'duration_minutes': 25,
    'task_description': 'Study calculus',
    'user_id': session['user_id']
}
```

---

## Progressive Web App (PWA)

### Manifest Configuration
Located in `static/manifest.json`
- **Display Mode**: Standalone (fullscreen app experience)
- **Theme Color**: #1a1a1a (garage dark)
- **Orientation**: Portrait (mobile-optimized)

### Installation
Users can install the app on mobile devices:
1. Open in mobile browser
2. Browser shows "Add to Home Screen" prompt
3. App installs like native app
4. Runs in standalone mode

---

## Error Handling

### Frontend Error Handling
- Form validation before API calls
- Network error handling with user feedback
- Session timeout detection
- Graceful degradation for API failures

### Backend Error Handling
- Input validation on all endpoints
- Database connection error handling
- Session validation on protected routes
- Proper HTTP status codes

---

## Security Considerations

### Authentication
- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection through Flask sessions

### Input Validation
- Server-side validation for all user inputs
- SQL injection prevention (NoSQL - MongoDB)
- XSS prevention through template escaping

### Environment Variables
- Sensitive data in `.env` file (not committed)
- Database URLs and secrets configurable
- Different configs for dev/prod environments

---

## Performance Considerations

### Database Optimization
- Indexed queries on user_id and car_model
- Minimal data fetching (only required fields)
- Connection pooling through Flask-PyMongo

### Frontend Optimization
- CDN for Tailwind CSS and Google Fonts
- Minimal JavaScript (no heavy frameworks)
- Efficient DOM manipulation
- Local state management for timer

### Mobile Optimization
- Mobile-first CSS design
- Touch-friendly interface elements
- Optimized for thumb zone interaction
- Minimal data usage

---

## 3D System Architecture

### Three.js Integration
The application includes a comprehensive 3D car viewing system using Three.js r128.

**Dependencies**:
- Three.js core library
- OrbitControls for camera interaction
- GLTFLoader for 3D model loading

**JavaScript Class**: `Car3DViewer` (located in `static/js/car-viewer-3d.js`)

### 3D Car Viewer Class

**Constructor Options**:
```javascript
new Car3DViewer('container-id', {
  width: 800,              // Viewer width
  height: 400,             // Viewer height
  enableControls: true,    // Enable mouse/touch controls
  autoRotate: false,       // Auto-rotate the model
  fallbackMode: 'image'    // Fallback when 3D unavailable
});
```

**Key Methods**:
- `loadCarModel(modelUrl, progress)`: Loads GLB/GLTF/FBX/OBJ models
- `updateProgress(progress)`: Updates car appearance based on restoration progress
- `enableFallback()`: Switches to emoji-based 2D visualization
- `applyProgressionEffects(progress)`: Applies rust-to-shine material changes
- `destroy()`: Cleans up Three.js resources

### 3D Model Loading Process

1. **API Request**: Fetch `/api/car_3d/{model_id}?progress={progress}`
2. **Response Processing**: Parse JSON response with model URLs
3. **File Loading**: Download and parse 3D model file
4. **Scene Setup**: Position, scale, and light the model
5. **Material Effects**: Apply progression-based visual changes
6. **Render Loop**: Continuous animation and user interaction

### Fallback System

**Triggers for Fallback Mode**:
- Three.js library not available
- No 3D model URL provided
- 3D model loading timeout (3 seconds)
- 3D model loading error

**Fallback Display**:
- Progress-based emoji cars (🚗💨 → 🔧🚗 → 🚙 → 🚗✨ → 🏁🚗🏁)
- Animated visual feedback
- User-friendly messaging

### 3D API Endpoint

#### Get 3D Model Data
**Endpoint**: `GET /api/car_3d/<model_id>`
**Parameters**: `?progress={progress_value}`

**Response**:
```json
{
  "model_3d_url": "/static/assets/uploads/3d/uuid_model.glb",
  "image_url": "/static/assets/uploads/2d/uuid_image.png",
  "description": "Half Restored",
  "progress": 50.0,
  "stage_threshold": 50
}
```

**Backend Logic**:
- Finds car template by model_id
- Determines current stage based on progress
- Returns appropriate asset URLs for that stage

---

## Admin Dashboard System

### Admin Authentication

#### Admin Session Management
- **Session Keys**: `is_admin=True`, `admin_user=username`
- **Authentication**: Separate from user authentication
- **Access Control**: All admin routes check `is_admin()` function

#### Default Credentials
- **Username**: `admin` (configurable via `ADMIN_USERNAME` env var)
- **Password**: `garage123` (configurable via `ADMIN_PASSWORD` env var)

### Admin Routes

#### Dashboard Routes
- `GET /admin/login` - Admin login page
- `POST /admin/login` - Process admin login
- `GET /admin/logout` - Admin logout
- `GET /admin` - Main admin dashboard
- `GET /admin/cars` - Car template management
- `GET /admin/cars/new` - Create new car form
- `POST /admin/cars/new` - Process new car creation
- `GET /admin/cars/<id>/edit` - Edit car template
- `POST /admin/cars/<id>/delete` - Delete car template
- `GET /admin/upload` - Asset upload interface
- `POST /admin/upload` - Process file upload

#### Admin API Routes
- `POST /api/admin/update_car_stage` - Update car stage assets

### Car Template Management

#### Creating New Car Templates
**Frontend Flow**:
1. Admin fills form with model_id, name, focus_time_required
2. System validates unique model_id
3. Creates car_template with 5 default stages
4. Redirects to edit page for asset upload

**Backend Logic**:
```python
new_car = {
    'model_id': 'ferrari_f40',
    'name': 'The Beast',
    'total_focus_minutes_required': 500,
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
```

---

## Asset Upload System

### File Upload Configuration
- **Max File Size**: 16MB
- **Upload Directory**: `static/assets/uploads/`
- **2D Images**: `static/assets/uploads/2d/`
- **3D Models**: `static/assets/uploads/3d/`

### Supported File Formats

#### 2D Images
- **Formats**: PNG, JPG, JPEG, GIF
- **Use Case**: Fallback visuals, thumbnails, previews
- **Recommended**: PNG (transparency), 512x512px to 1024x1024px

#### 3D Models
- **GLB** (preferred): Binary GLTF, compact, includes textures
- **GLTF**: JSON GLTF, human-readable, multiple files
- **FBX**: Autodesk format, widely supported
- **OBJ**: Wavefront format, basic geometry only

### File Upload Process

#### Frontend Upload Flow
1. Admin selects file via drag-drop or file picker
2. Form validates file type and size
3. Auto-detects asset type (2D vs 3D) from extension
4. Optional: Assigns to specific car and stage
5. Uploads with unique filename generation

#### Backend Processing
```python
# Generate unique filename
filename = secure_filename(file.filename)
unique_filename = f"{uuid.uuid4()}_{filename}"

# Determine upload path
if asset_type == '3d':
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], '3d')
else:
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], '2d')

# Save file
file.save(os.path.join(upload_path, unique_filename))

# Update database if assigned to car
if car_id and stage_threshold:
    update_field = 'model_3d_url' if asset_type == '3d' else 'image_url'
    file_url = f"/static/assets/uploads/{asset_type}/{unique_filename}"
    
    # Update specific stage in car template
    mongo.db.car_templates.update_one(
        {'_id': ObjectId(car_id), 'stages.threshold': stage_threshold},
        {'$set': {f'stages.$.{update_field}': file_url}}
    )
```

### Asset Management

#### Database Integration
Assets are linked to car templates via URLs in the `stages` array:
```json
{
  "threshold": 50,
  "image_url": "/static/assets/uploads/2d/abc123_mustang_50.png",
  "model_3d_url": "/static/assets/uploads/3d/def456_mustang_50.glb",
  "description": "Half Restored"
}
```

#### Admin Asset Interface
- **Visual indicators**: Shows which stages have assets (🖼️ = 2D, 📦 = 3D, ❌ = Missing)
- **Preview functionality**: 2D images show thumbnails, 3D shows file info
- **Remove assets**: Delete files and update database
- **Replace assets**: Upload new versions

---

## Environment Configuration

### New Environment Variables (.env)

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-change-in-production
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=True

# MongoDB Connection
MONGO_URI=mongodb://localhost:27017/garage_focus

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=garage123

# Game Configuration
MIN_FOCUS_DURATION=5                     # Minimum minutes for progress
TOTAL_MINUTES_FOR_100_PERCENT=300       # Minutes required for 100% completion
SCRAP_METAL_PER_MINUTE=1                # Currency earned per minute
GRACE_PERIOD=10                         # Seconds allowed when switching tabs
```

### Configuration Loading
```python
# Load environment variables from .env file
load_dotenv()

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
```

---

## Updated Tech Stack

### Backend Technologies
- **Python Flask**: Web framework
- **Flask-PyMongo**: MongoDB integration
- **Werkzeug**: Password hashing and file handling
- **Python-dotenv**: Environment variable management
- **UUID**: Unique filename generation

### Frontend Technologies
- **Three.js r128**: 3D graphics rendering
- **OrbitControls**: Camera interaction
- **GLTFLoader**: 3D model loading
- **HTML5 File API**: File upload handling
- **Page Visibility API**: Tab detection
- **Tailwind CSS**: Styling framework

### Database & Storage
- **MongoDB**: Document database for app data
- **File System**: Asset storage for uploaded files
- **Session Storage**: Flask sessions for authentication

---

## Complete API Reference

### User API Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Main garage view |
| GET/POST | `/login` | User authentication |
| GET/POST | `/register` | User registration |
| GET | `/logout` | User logout |
| GET | `/junkyard` | Car selection page |
| POST | `/api/select_car` | Choose car from junkyard |
| POST | `/api/start_session` | Begin focus session |
| POST | `/api/complete_session` | End focus session |
| POST | `/api/heartbeat` | Session keep-alive |

### 3D System API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/car_3d/<model_id>` | Get 3D model data for car stage |

### Admin API Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `/admin/login` | Admin authentication |
| GET | `/admin/logout` | Admin logout |
| GET | `/admin` | Admin dashboard |
| GET | `/admin/cars` | Car template management |
| GET/POST | `/admin/cars/new` | Create new car template |
| GET | `/admin/cars/<id>/edit` | Edit car template |
| POST | `/admin/cars/<id>/delete` | Delete car template |
| GET/POST | `/admin/upload` | Asset upload interface |
| POST | `/api/admin/update_car_stage` | Update car stage assets |

---

## System Initialization

### Default Data Creation
On first run, the system automatically creates:

#### Default Car Templates
```python
templates = [
    {
        "model_id": "mustang_1969",
        "name": "The Stallion",
        "total_focus_minutes_required": 300,
        "stages": [...] # 5 stages with empty asset URLs
    },
    {
        "model_id": "corvette_1965", 
        "name": "The Stingray",
        "total_focus_minutes_required": 400,
        "stages": [...] # 5 stages with empty asset URLs
    }
]
```

#### Directory Structure Creation
```python
# Ensure upload directories exist
os.makedirs('static/assets/uploads/2d', exist_ok=True)
os.makedirs('static/assets/uploads/3d', exist_ok=True)
```

---

## Error Handling & Debugging

### 3D System Error Handling
- **Timeout mechanism**: 3-second timeout for 3D loading
- **Graceful degradation**: Automatic fallback to 2D mode
- **Resource cleanup**: Proper Three.js memory management
- **Cross-browser compatibility**: WebGL support detection

### Admin System Error Handling
- **File validation**: Server-side file type and size checks
- **Permission checks**: Admin authentication on all admin routes
- **Database error handling**: Proper error messages for database operations
- **Upload error handling**: File system error catching and reporting

### Debug Logging
```python
# Enable debug mode for development
if APP_CONFIG['FLASK_DEBUG']:
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('Debug mode enabled')
```

---

This technical documentation now provides complete coverage of the enhanced Garage Focus application, including all 3D features, admin dashboard functionality, and asset management systems.
