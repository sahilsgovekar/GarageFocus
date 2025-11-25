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

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- MongoDB (local installation or MongoDB Atlas account)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd habit-tracker-with-car
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   
   **Option A: Local MongoDB**
   - Install MongoDB locally
   - The app will use `mongodb://localhost:27017/garage_focus` by default
   
   **Option B: MongoDB Atlas (Cloud)**
   - Create a free MongoDB Atlas account
   - Get your connection string
   - Set environment variable:
     ```bash
     export MONGO_URI="your-mongodb-atlas-connection-string"
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Register a new account
   - Select your first project car
   - Start focusing!

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
