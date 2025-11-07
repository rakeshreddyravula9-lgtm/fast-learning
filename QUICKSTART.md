# Quick Start Guide - Fast Learning

Get up and running in 5 minutes!

## 🎯 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git (for cloning)

## ⚡ Installation Steps

### Step 1: Navigate to Project
```bash
cd fast-learning
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as it downloads AI models.

### Step 4: Run the Application
```bash
cd backend
python app.py
```

You should see:
```
✓ Local AI model loaded successfully
 * Running on http://0.0.0.0:5000
```

### Step 5: Open in Browser
Open your web browser and navigate to:
```
http://localhost:5000
```

## 🎨 First Use

1. **Welcome Screen**: You'll see example prompts to get started
2. **Type a Message**: Enter any question in the chat box
3. **Watch AI Respond**: See the response stream in real-time
4. **Try Different Models**: Use the dropdown to switch AI models

## 🔑 Optional: OpenAI API Setup

For best quality responses with GPT-3.5/GPT-4:

1. Get API key from https://platform.openai.com/api-keys
2. Create `.env` file in project root:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```
3. Restart the application

**Without API key**: The app uses local AI models (free, works offline)

## 🚀 Usage Tips

### Keyboard Shortcuts
- `Enter` - Send message
- `Shift + Enter` - New line in message

### Features to Try
1. **New Chat**: Click "+ New Chat" button
2. **Dark Mode**: Click moon/sun icon in header
3. **Change Model**: Select from dropdown (GPT-3.5, GPT-4, Local)
4. **View History**: Click conversations in sidebar
5. **Delete Chat**: Hover over conversation, click trash icon

### Example Prompts
```
🔹 "Explain machine learning in simple terms"
🔹 "Write a Python function to sort a list"
🔹 "What are the top 5 programming languages in 2024?"
🔹 "Help me debug this code: [paste your code]"
🔹 "Write a business email about project delay"
```

## 📱 Mobile Access

Access from any device on your network:

1. Find your IP address:
```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

2. Open on mobile browser:
```
http://YOUR_IP_ADDRESS:5000
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Change port in backend/app.py (last line):
socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

### Module Not Found Error
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Slow First Response
- First run downloads AI model (~1GB)
- Subsequent responses are faster
- Use OpenAI API for instant responses

### Can't Connect WebSocket
- Check firewall settings
- Ensure port 5000 is not blocked
- Try using 127.0.0.1:5000 instead of localhost:5000

## 📊 System Requirements

### Minimum
- 4GB RAM
- 2GB free disk space
- Python 3.12+
- Modern web browser

### Recommended
- 8GB RAM
- 5GB free disk space
- SSD for faster model loading
- Chrome/Firefox latest version

## 🎓 Next Steps

1. ✅ **Read Full Documentation**: Check `README.md`
2. 🔧 **Configure Settings**: Edit `.env` file
3. 🌐 **Deploy Online**: Use services like Heroku, Railway, or DigitalOcean
4. 🎨 **Customize UI**: Edit `frontend/css/style.css`
5. 🤖 **Add Models**: Explore different Hugging Face models

## 🆘 Need Help?

- **Documentation**: Read `README.md`
- **Issues**: Check GitHub Issues
- **Contact**: rakeshreddyravula9@gmail.com

## 🎉 You're Ready!

Start chatting with AI and explore the features. Enjoy!

---

**Made with ❤️ by Rakesh Reddy Ravula**
