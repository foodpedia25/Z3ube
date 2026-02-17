# Z3ube Quick Start Guide

## 🚀 Getting Started

### Backend Setup

1. **Navigate to project directory:**
   ```bash
   cd /Volumes/BUFFALO/Z3ube
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   - `OPENAI_API_KEY=your_key_here`
   - `ANTHROPIC_API_KEY=your_key_here`
   - `GOOGLE_API_KEY=your_key_here`

5. **Start the backend server:**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   API docs at: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd /Volumes/BUFFALO/Z3ube/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:3000`

## 🎯 Try It Out

Once both servers are running:

1. **Visit the landing page:** `http://localhost:3000`
   - See the stunning Matrix rain background
   - Explore capability cards

2. **Try the chat interface:** `http://localhost:3000/chat`
   - Ask complex questions
   - Request code generation
   - See thinking steps in action

3. **View the dashboard:** `http://localhost:3000/dashboard`
   - Monitor system metrics
   - See learning statistics
   - Check auto-healer status

## 🧪 Test Examples

### Chat Examples:
- "Explain quantum computing in simple terms"
- "What are the differences between Python and JavaScript?"
- "How does blockchain technology work?"

### Code Generation:
- "Generate Python code for a binary search tree with insert, search, and delete methods"
- "Create a React component for a todo list with TypeScript"
- "Write ROS2 code for a robot navigation node"

### Research:
- "Research the latest developments in artificial intelligence"
- "What are the current trends in web development?"

## 📦 Deployment

### Backend (Railway/Render)
1. Push code to GitHub
2. Connect repository
3. Set environment variables
4. Deploy

### Frontend (Vercel)
1. Import from GitHub
2. Set `NEXT_PUBLIC_API_URL` to deployed backend URL
3. Deploy

## 🌟 Key Features

✅ **Reasoning** - Multi-step chain-of-thought  
✅ **Research** - Deep multi-source analysis  
✅ **Code Gen** - Multiple languages + robotics  
✅ **Self-Learning** - Improves over time  
✅ **Auto-Healing** - Automatic error recovery  
✅ **Matrix UI** - Stunning visual experience  

Enjoy your next-generation AI agent! 🚀
