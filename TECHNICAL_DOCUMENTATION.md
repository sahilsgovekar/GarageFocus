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
  "model_id": String (unique),
  "name": String,
  "total_focus_minutes_required": Number,
  "stages": [
    {
      "threshold": Number (0-100),
      "image_url": String,
      "description": String
    }
  ]
}
```

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

This technical documentation provides a complete overview of how Garage Focus works under the hood, from user interactions to database updates.
