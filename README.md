# Fast Learning

A full-stack conversational AI learning platform built with Flask and modern web technologies. Features real-time chat with WebSocket support, conversation history, universal knowledge system, and multiple AI model support.

![Fast Learning](https://img.shields.io/badge/AI-Fast%20Learning-10a37f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0.0-black?style=for-the-badge)
![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-orange?style=for-the-badge)

## ✨ Features

### 🤖 AI Capabilities
- **Multiple AI Models**: Support for GPT-3.5, GPT-4, and local Hugging Face models
- **Real-time Streaming**: See AI responses as they're generated
- **Context-Aware**: Maintains conversation history for coherent responses
- **Smart Fallback**: Automatically switches between OpenAI, local models, and rule-based responses

### 💬 Chat Features
- **Modern AI Chat Interface**: Clean, intuitive interface with gradient design
- **Conversation Management**: Save, load, and delete chat sessions
- **Message History**: Persistent storage of all conversations
- **Typing Indicators**: Real-time feedback during AI response generation
- **Code Highlighting**: Syntax highlighting for code snippets
- **Markdown Support**: Formatted text with bold, italic, and code blocks

### 🎨 User Experience
- **Dark/Light Theme**: Toggle between themes with persistence
- **Responsive Design**: Works on desktop, tablet, and mobile
- **WebSocket Support**: Real-time bidirectional communication
- **Example Prompts**: Quick-start suggestions for new users
- **Session Persistence**: Conversations saved automatically

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)
- Optional: OpenAI API key for GPT models

### Installation

1. **Clone or navigate to the repository**
```bash
cd fast-learning
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Optional: Set OpenAI API key** (for GPT models)
```bash
export OPENAI_API_KEY='your-api-key-here'
```
Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

5. **Run the application**
```bash
cd backend
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
fast-learning/
├── backend/
│   ├── app.py                      # Flask application with WebSocket
│   ├── conversations/              # Stored conversation JSON files
│   ├── models/                     # AI model configurations
│   └── utils/
│       ├── ai_engine.py           # AI model integration
│       └── conversation_manager.py # Conversation storage logic
├── frontend/
│   ├── index.html                 # Main HTML structure
│   ├── css/
│   │   └── style.css             # Modern UI styling
│   └── js/
│       └── app.js                # Frontend logic & WebSocket client
├── data/                          # Additional data storage
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── QUICKSTART.md                  # Quick setup guide
└── LICENSE                        # MIT License
```

## 🌍 Deploy to Cloud (Get Your Public URL)

Your Fast Learning platform can be deployed to the cloud and accessible from anywhere with a public URL like `https://your-app.onrender.com`.

### Option 1: Deploy to Render.com (Recommended - FREE)

Render offers free hosting with automatic HTTPS and custom domains.

#### Steps:

1. **Push your code to GitHub**
   ```bash
   # If not already initialized
   git init
   git add .
   git commit -m "Ready for deployment"
   
   # Create repository on GitHub, then:
   git remote add origin https://github.com/yourusername/fast-learning.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Visit [https://render.com](https://render.com) and sign up
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration
   - Click **"Deploy"**
   - Your app will be live at: `https://fast-learning-xxxx.onrender.com`

3. **Add Environment Variables (Optional)**
   - In Render dashboard, go to **Environment** tab
   - Add: `OPENAI_API_KEY` = `your-api-key` (for GPT models)

#### Features:
- ✅ Free tier available
- ✅ Automatic HTTPS/SSL
- ✅ Custom domain support
- ✅ Auto-deploy from GitHub
- ✅ Zero configuration needed

### Option 2: Deploy to Railway.app (FREE with $5 credit)

Railway provides instant deployments with generous free tier.

#### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Railway**
   - Visit [https://railway.app](https://railway.app)
   - Click **"Start a New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your `fast-learning` repository
   - Railway auto-detects Python and deploys
   - Get your URL: `https://fast-learning.up.railway.app`

3. **Configure Environment**
   - Click on your service → **Variables** tab
   - Add `OPENAI_API_KEY` if using GPT models

### Option 3: Deploy to Heroku

Heroku is a mature platform with extensive documentation.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create fast-learning-ai
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your-api-key
   ```

5. **Open Your App**
   ```bash
   heroku open
   ```
   - URL: `https://fast-learning-ai.herokuapp.com`

### Custom Domain (Optional)

Once deployed, you can add a custom domain like `fastlearning.ai`:

1. **Purchase Domain** (Namecheap, GoDaddy, Google Domains)
2. **Add to Platform**:
   - **Render**: Dashboard → Settings → Custom Domains
   - **Railway**: Project Settings → Domains
   - **Heroku**: `heroku domains:add www.yourname.com`
3. **Configure DNS**:
   - Add CNAME record pointing to your platform's URL
   - SSL certificates are automatic on all platforms

### Production Checklist

Before going live, ensure:
- ✅ `debug=False` in `app.py` (already set)
- ✅ Environment variables configured (OpenAI API key)
- ✅ CORS settings updated for production domain
- ✅ Error logging enabled
- ✅ Database backup strategy (if using database)

## 🔧 Configuration

### AI Models

The platform supports multiple AI providers:

1. **OpenAI (GPT-3.5/GPT-4)**
   - Requires API key in `.env` file
   - Best quality responses
   - Usage charges apply

2. **Hugging Face (Local Models)**
   - Free to use
   - Runs locally (DialoGPT-medium by default)
   - No API key required
   - First run downloads model (~1GB)

3. **Rule-Based Fallback**
   - Always available
   - Pattern-matching responses
   - No setup required

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration (optional)
OPENAI_API_KEY=your-api-key-here

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Model Settings
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## 🌐 API Endpoints

### REST API

- `GET /api/health` - Health check
- `POST /api/chat` - Send message (non-streaming)
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/<id>` - Get specific conversation
- `DELETE /api/conversations/<id>` - Delete conversation
- `POST /api/conversations/clear` - Clear all conversations
- `GET /api/models` - List available AI models

### WebSocket Events

**Client → Server:**
- `send_message` - Send chat message
- `new_conversation` - Create new conversation

**Server → Client:**
- `connected` - Connection established
- `typing` - AI is typing indicator
- `message_chunk` - Streaming response chunk
- `message_complete` - Response finished
- `conversation_created` - New conversation created
- `error` - Error occurred

## 💡 Usage Examples

### Basic Chat
1. Open the application in your browser
2. Type a message in the input box
3. Press Enter or click Send
4. Watch the AI response stream in real-time

### Switch AI Models
- Use the dropdown in the header to select different models
- Choose between GPT-3.5, GPT-4, or local models
- Model preference is saved per conversation

### Manage Conversations
- **New Chat**: Click "New Chat" button in sidebar
- **Load Chat**: Click on any conversation in the sidebar
- **Delete Chat**: Hover over conversation and click trash icon
- **Clear All**: Click "Clear All Chats" at bottom of sidebar

### Example Prompts

Try these example prompts:
- "Explain quantum computing in simple terms"
- "Write a Python function to reverse a string"
- "Give me tips for learning AI and machine learning"
- "What are the best practices for web development?"

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **Flask-SocketIO** - WebSocket support
- **OpenAI API** - GPT models integration
- **Transformers** - Hugging Face model support
- **PyTorch** - Deep learning framework
- **NLTK** - Natural language processing

### Frontend
- **HTML5/CSS3** - Modern web standards
- **Vanilla JavaScript** - No framework dependencies
- **Socket.IO Client** - Real-time communication
- **Marked.js** - Markdown rendering
- **Highlight.js** - Code syntax highlighting
- **Font Awesome** - Icon library

## 📊 Performance

- **Response Time**: < 2s for GPT-3.5, < 5s for local models
- **Streaming**: Real-time chunk delivery
- **Concurrent Users**: Supports multiple simultaneous connections
- **Storage**: JSON-based, scalable to thousands of conversations

## 🔒 Security Notes

- API keys stored in environment variables (never in code)
- CORS enabled for development (configure for production)
- Input sanitization for XSS prevention
- Rate limiting recommended for production deployment

## 🚧 Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Voice input/output
- [ ] Image generation integration (DALL-E)
- [ ] Export conversations (PDF, Markdown, JSON)
- [ ] Custom system prompts
- [ ] Fine-tuned models
- [ ] Analytics dashboard
- [ ] Mobile app (React Native/Flutter)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Rakesh Reddy Ravula**
- GitHub: [@rakeshreddyravula9-lgtm](https://github.com/rakeshreddyravula9-lgtm)
- Email: rakeshreddyravula9@gmail.com

## 🙏 Acknowledgments

- OpenAI for GPT API
- Hugging Face for transformer models
- Flask and Socket.IO communities
- Modern AI chat interface design

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using Python, Flask, and modern web technologies**
