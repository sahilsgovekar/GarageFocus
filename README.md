# 🏁 Garage Focus - Fix Cars, Fix Focus

A gamified productivity web app where you restore digital cars by maintaining focus. Built with Flask, MongoDB, and modern web technologies.

## 🚗 Core Concept

"Don't let the engine stall." Transform rusted junk cars into showroom classics by completing focused work sessions. Stay focused or drop the wrench!

## ✨ Features

- **🔧 Focus Sessions**: Pomodoro-style focus timer with tab switching detection
- **🚗 Car Restoration**: Visual progress as cars transform from rust buckets to beauties
- **🔩 Scrap Metal Currency**: Earn currency for completing focus sessions
- **📱 Mobile-First PWA**: Responsive design that works great on phones
- **🏆 Showroom Collection**: Build your garage of completed restorations
- **⚠️ Anti-Distraction**: Leave the tab and risk failing your session!

## 🛠️ Tech Stack

- **Backend**: Python Flask with Flask-PyMongo
- **Database**: MongoDB (local or Atlas)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **PWA**: Service worker ready, mobile installable
- **Focus Detection**: Page Visibility API

## 🚀 Local Setup & Installation

### Prerequisites

- **Python 3.7+** (Python 3.8+ recommended)
- **MongoDB** (local installation OR MongoDB Atlas account)
- **Git** (for cloning the repository)

### Step 1: Clone & Navigate

```bash
# Clone the repository
git clone <repository-url>
cd habit-tracker-with-car

# Or if you have the files already, just navigate to the directory
cd habit-tracker-with-car
```

### Step 2: Set Up Virtual Environment

**Why use a virtual environment?**
- Keeps dependencies isolated from your system Python
- Prevents version conflicts with other projects
- Makes the project more portable

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
# Make sure your virtual environment is activated (you should see (venv) in prompt)
pip install -r requirements.txt
```

**Dependencies installed:**
- Flask 2.3.3 (Web framework)
- Flask-PyMongo 2.3.0 (MongoDB integration)
- pymongo 4.6.0 (MongoDB driver)
- Werkzeug 2.3.7 (Security utilities)
- python-dotenv 1.0.0 (Environment variables)

### Step 4: Set Up Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred text editor
```

**Required configuration in `.env`:**
```bash
# Change this to a secure random string
FLASK_SECRET_KEY=your-super-secret-key-here

# MongoDB connection (choose one option below)
MONGO_URI=mongodb://localhost:27017/garage_focus
```

**For a secure secret key, you can generate one:**
```bash
# Generate a random secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Set Up Database

#### Option A: Local MongoDB (Recommended for Development)

**Install MongoDB:**
```bash
# On macOS with Homebrew:
brew tap mongodb/brew
brew install mongodb-community@8.0

# On Ubuntu/Debian:
wget -qO - https://www.mongodb.org/static/pgp/server-8.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# On Windows:
# Download from https://www.mongodb.com/try/download/community
```

**Start MongoDB:**
```bash
# On macOS:
brew services start mongodb-community@8.0

# On Ubuntu/Linux:
sudo systemctl start mongod
sudo systemctl enable mongod  # Start on boot

# On Windows:
# MongoDB should start automatically as a service
```

**Verify MongoDB is running:**
```bash
# Check if MongoDB is listening on port 27017
netstat -an | grep 27017

# Or connect using MongoDB shell
mongosh  # Should connect to mongodb://127.0.0.1:27017
```

#### Option B: MongoDB Atlas (Cloud Database)

**Set up MongoDB Atlas:**
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for a free account
3. Create a new cluster (free tier available)
4. Create a database user with read/write permissions
5. Get your connection string

**Update your `.env` file:**
```bash
# Replace with your actual Atlas connection string
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/garage_focus?retryWrites=true&w=majority
```

### Step 6: Run the Application

```bash
# Make sure you're in the project directory and virtual environment is activated
source venv/bin/activate  # If not already activated

# Run the Flask application
python app.py
```

**Expected output:**
```
* Serving Flask app 'app'
* Debug mode: on
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:8000
* Running on http://192.168.0.X:8000
```

**If port 5000 is in use (common on macOS):**
The app is configured to run on port 8000 by default. If you need to change it, update the `.env` file:
```bash
FLASK_PORT=3000  # or any available port
```

### Step 7: Test the Application

1. **Open your web browser**
   - Navigate to `http://localhost:8000`
   - You should see the login page

2. **Create an account**
   - Click "Get Your License"
   - Fill out the registration form
   - You'll be redirected to the junkyard

3. **Select your first car**
   - Choose between "The Stallion" (Mustang) or "The Stingray" (Corvette)
   - Click "SELECT" and confirm your choice

4. **Start your first focus session**
   - Enter what you're working on (e.g., "Reading documentation")
   - Select a duration (try 5 or 10 minutes for testing)
   - Click "🔧 START ENGINE"

5. **Test the focus detection**
   - Switch to another tab - you should see a warning
   - Return within 10 seconds to continue the session
   - Or stay away longer to see the session fail

### Step 8: Stop the Application

```bash
# In the terminal where the app is running:
Ctrl+C  # This stops the Flask development server

# To deactivate the virtual environment:
deactivate
```

### Step 9: MongoDB Management (Optional)

**View your data:**
```bash
# Connect to MongoDB shell
mongosh

# Switch to the garage_focus database
use garage_focus

# View collections
show collections

# View users
db.users.find()

# View cars
db.user_cars.find()

# View car templates
db.car_templates.find()
```

---

## 📱 Mobile Installation (PWA)

The app works great on mobile devices and can be installed as a Progressive Web App:

### On iOS:
1. Open Safari and navigate to `http://your-ip:8000`
2. Tap the Share button
3. Select "Add to Home Screen"
4. The app icon will appear on your home screen

### On Android:
1. Open Chrome and navigate to `http://your-ip:8000`
2. Tap the three-dot menu
3. Select "Add to Home Screen" or "Install App"
4. The app will install like a native app

---

## 🛠️ Development Tips

### Virtual Environment Management
```bash
# Always activate your virtual environment when working on the project
source venv/bin/activate

# Install new packages (they'll be saved to requirements.txt)
pip install package-name
pip freeze > requirements.txt

# Deactivate when done
deactivate
```

### Database Reset
```bash
# If you want to reset all data
mongosh
use garage_focus
db.dropDatabase()
```

### Port Issues
```bash
# Find what's using port 5000 (common on macOS for AirPlay)
lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>

# Or just use a different port in .env
FLASK_PORT=8000
```

### Environment Variables
```bash
# View all environment variables being used
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print([k for k in os.environ.keys() if 'FLASK' in k or 'MONGO' in k])"
```

---

## 🚨 Troubleshooting

### Common Issues:

**"ModuleNotFoundError: No module named 'flask'"**
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt`

**"Connection refused (MongoDB)"**
- Make sure MongoDB is running: `brew services start mongodb-community@8.0`
- Check if port 27017 is open: `netstat -an | grep 27017`

**"Port 5000 is in use"**
- The app runs on port 8000 by default
- Disable AirPlay Receiver in System Preferences → Sharing (macOS)
- Or use a different port in `.env`

**"Command not found: python"**
- Use `python3` instead of `python`
- Make sure Python 3.7+ is installed

**Virtual environment issues**
- Delete the venv folder and recreate: `rm -rf venv && python3 -m venv venv`

---

## 📂 Project Structure After Setup

```
garage-focus/
├── venv/                  # Virtual environment (ignored by git)
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Your local environment config (ignored by git)
├── .env.example          # Example environment config (committed)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── TECHNICAL_DOCUMENTATION.md  # Technical details
├── templates/            # HTML templates
│   ├── base.html         # Base template with focus timer
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── garage.html       # Main garage interface
│   └── junkyard.html     # Car selection
└── static/              # Static assets
    └── manifest.json    # PWA manifest
```

Now you're ready to start restoring digital cars and building focus! 🏁🔧

## 🎮 How to Play

1. **Register** - Get your garage license
2. **Visit Junkyard** - Pick a project car (Mustang or Corvette)
3. **Start Focus Session** - Choose your task and duration
4. **Stay Focused** - Don't switch tabs or the engine stalls!
5. **Earn Progress** - Complete sessions to restore your car
6. **Build Collection** - Complete cars go to your showroom

## 📱 Mobile Installation

The app is a Progressive Web App (PWA):

1. Open the app in your mobile browser
2. Tap "Add to Home Screen" or "Install App"
3. Use it like a native mobile app!

## 🔧 Focus Rules

- **Stay Active**: Keep the browser tab focused during sessions
- **10-Second Grace**: Brief tab switches give you 10 seconds to return
- **Session Failure**: Stay away too long = dropped wrench = no progress
- **Minimum Time**: Need at least 5 minutes focused for progress
- **Fair Rewards**: 1 minute focused = 1 scrap metal earned

## 🏗️ Project Structure

```
garage-focus/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template with timer
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── garage.html       # Main garage interface
│   └── junkyard.html     # Car selection
├── static/              # Static assets
│   └── manifest.json    # PWA manifest
└── README.md           # This file
```

## 🎨 Design Philosophy

- **Mobile-First**: Thumb-zone navigation, vertical scrolling
- **Dark Theme**: Garage aesthetic with neon accents
- **Visual Feedback**: Smooth transitions and progress indicators
- **Gamification**: Clear rewards and progression system

## 🚧 Future Enhancements

- [ ] Real car images instead of emojis
- [ ] More car models and customization options
- [ ] Leaderboards and social features
- [ ] Advanced statistics and insights
- [ ] Sound effects and animations
- [ ] Streak tracking and achievements

## 🤝 Contributing

This is a demo project built for learning purposes. Feel free to fork and enhance!

## 📄 License

Open source - feel free to use and modify!

---

**Remember**: Don't let your engine stall! 🏁🔧
