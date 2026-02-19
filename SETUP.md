# Z3ube - Setup Instructions

## ⚠️ Important Note on Python Version

Z3ube requires **Python 3.10 or 3.11** due to compatibility issues with some dependencies.

If you have Python 3.13, please install Python 3.11:
```bash
# Using Homebrew (macOS)
brew install python@3.11

# Then create venv with Python 3.11
/usr/local/bin/python3.11 -m venv venv
```

## 🚀 Quick Setup (After Python 3.11 is installed)

### 1. Backend Setup

```bash
cd /Volumes/BUFFALO/Z3ube

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Add Your API Keys

Edit `/Volumes/BUFFALO/Z3ube/.env` and add your API keys:

```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here

# Optional: Cloud Database (Supabase/PostgreSQL)
# If not provided, Z3ube uses local SQLite (not persistent on Vercel)
DATABASE_URL=postgresql://user:password@host:port/database
```

### 3. Start Backend Server

```bash
cd /Volumes/BUFFALO/Z3ube
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

### 4. Frontend Setup

In a new terminal:

```bash
cd /Volumes/BUFFALO/Z3ube/frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend will run at: `http://localhost:3000`

## 🎯 Access Z3ube

- **Landing Page**: http://localhost:3000
- **Chat Interface**: http://localhost:3000/chat
- **Neural Dashboard**: http://localhost:3000/dashboard
- **Robotics Studio**: http://localhost:3000/robotics
- **Knowledge Graph**: http://localhost:3000/knowledge
- **API Docs**: http://localhost:8000/docs

## ✅ What to Expect

- **Matrix Rain Background**: Animated green digital rain
- **Advanced Chat**: Ask complex questions and see thinking steps
- **Self-Learning**: The system learns from every interaction
- **Robotics Studio**: Generate full ROS2 project structures
- **3D Knowledge Graph**: Visualize the AI's internal state
- **Dashboard**: View real-time system metrics

Enjoy your next-generation World-Class AI agent! 🚀🌍
