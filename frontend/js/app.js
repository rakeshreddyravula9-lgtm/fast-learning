// API Base URL - automatically detect if local or production
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : window.location.origin;

// Global state
let currentSessionId = null;
let socket = null;
let conversations = [];
let currentModel = 'gpt-3.5-turbo';
let isStreaming = false;
let currentUser = null;
let sessionToken = null;

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    toggleSidebar: document.getElementById('toggleSidebar'),
    newChatBtn: document.getElementById('newChatBtn'),
    clearAllBtn: document.getElementById('clearAllBtn'),
    conversationsList: document.getElementById('conversationsList'),
    chatContainer: document.getElementById('chatContainer'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    typingIndicator: document.getElementById('typingIndicator'),
    modelSelector: document.getElementById('modelSelector'),
    modelBadge: document.getElementById('modelBadge'),
    chatTitle: document.getElementById('chatTitle'),
    themeToggle: document.getElementById('themeToggle')
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    initializeTheme();
    initializeWebSocket();
    loadConversations();
    attachEventListeners();
    autoResizeTextarea();
});

// Check if user is authenticated
async function checkAuthentication() {
    sessionToken = localStorage.getItem('session_token') || sessionStorage.getItem('session_token');
    
    if (!sessionToken) {
        window.location.href = '/login';
        return;
    }
    
    // Verify session
    try {
        const response = await fetch(`${API_URL}/api/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_token: sessionToken })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            updateUserInterface();
        } else {
            // Session invalid, redirect to login
            localStorage.removeItem('session_token');
            sessionStorage.removeItem('session_token');
            localStorage.removeItem('user_data');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Authentication error:', error);
        window.location.href = '/login';
    }
}

// Update UI with user information
function updateUserInterface() {
    if (currentUser) {
        // Update header with user name
        const chatTitle = document.getElementById('chatTitle');
        if (chatTitle.textContent === 'Fast Learning') {
            chatTitle.textContent = `Welcome, ${currentUser.username}!`;
        }
        
        // Add logout button if not exists
        const headerActions = document.querySelector('.header-actions');
        if (!document.getElementById('logoutBtn')) {
            const logoutBtn = document.createElement('button');
            logoutBtn.id = 'logoutBtn';
            logoutBtn.className = 'btn-theme-toggle';
            logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i>';
            logoutBtn.title = 'Logout';
            logoutBtn.addEventListener('click', handleLogout);
            headerActions.appendChild(logoutBtn);
        }
    }
}

// Handle logout
async function handleLogout() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    try {
        await fetch(`${API_URL}/api/auth/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_token: sessionToken })
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Clear local storage
        localStorage.removeItem('session_token');
        sessionStorage.removeItem('session_token');
        localStorage.removeItem('user_data');
        
        // Redirect to login
        window.location.href = '/login';
    }
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    elements.themeToggle.innerHTML = theme === 'light' 
        ? '<i class="fas fa-moon"></i>' 
        : '<i class="fas fa-sun"></i>';
}

// WebSocket Connection
function initializeWebSocket() {
    socket = io(API_URL);
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
    
    socket.on('connected', (data) => {
        console.log('Session ID:', data.session_id);
    });
    
    socket.on('typing', (data) => {
        if (data.is_typing) {
            showTypingIndicator();
        } else {
            hideTypingIndicator();
        }
    });
    
    socket.on('message_chunk', (data) => {
        appendMessageChunk(data.chunk);
    });
    
    socket.on('message_complete', (data) => {
        hideTypingIndicator();
        isStreaming = false;
        scrollToBottom();
    });
    
    socket.on('conversation_created', (data) => {
        currentSessionId = data.session_id;
        loadConversations();
    });
    
    socket.on('error', (data) => {
        console.error('Socket error:', data.error);
        showError(data.error);
        hideTypingIndicator();
        isStreaming = false;
    });
}

// Event Listeners
function attachEventListeners() {
    // Sidebar toggle
    elements.toggleSidebar.addEventListener('click', () => {
        elements.sidebar.classList.toggle('visible');
    });
    
    // New chat
    elements.newChatBtn.addEventListener('click', createNewChat);
    
    // Clear all
    elements.clearAllBtn.addEventListener('click', clearAllConversations);
    
    // Send message
    elements.sendBtn.addEventListener('click', sendMessage);
    
    // Enter key to send
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Model selector
    elements.modelSelector.addEventListener('change', (e) => {
        currentModel = e.target.value;
        updateModelBadge();
    });
    
    // Theme toggle
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // Example prompts
    document.querySelectorAll('.prompt-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            elements.messageInput.value = prompt;
            sendMessage();
        });
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    elements.messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
}

// Conversations Management
async function loadConversations() {
    try {
        const response = await fetch(`${API_URL}/api/conversations`);
        const data = await response.json();
        conversations = data.conversations;
        renderConversations();
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

function renderConversations() {
    if (conversations.length === 0) {
        elements.conversationsList.innerHTML = `
            <div style="padding: 20px; text-align: center; color: rgba(255,255,255,0.5); font-size: 14px;">
                No conversations yet
            </div>
        `;
        return;
    }
    
    elements.conversationsList.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.session_id === currentSessionId ? 'active' : ''}" 
             data-session-id="${conv.session_id}">
            <span class="title">${conv.title}</span>
            <button class="delete-btn" data-session-id="${conv.session_id}">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
    
    // Attach click handlers
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.delete-btn')) {
                loadConversation(item.dataset.sessionId);
            }
        });
    });
    
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteConversation(btn.dataset.sessionId);
        });
    });
}

async function loadConversation(sessionId) {
    try {
        const response = await fetch(`${API_URL}/api/conversations/${sessionId}`);
        const conversation = await response.json();
        
        currentSessionId = sessionId;
        elements.welcomeScreen.classList.add('hidden');
        elements.messages.innerHTML = '';
        
        // Update title
        elements.chatTitle.textContent = conversation.title;
        
        // Render messages
        conversation.messages.forEach(msg => {
            displayMessage(msg.role, msg.content, false);
        });
        
        renderConversations();
        scrollToBottom();
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

function createNewChat() {
    currentSessionId = null;
    elements.welcomeScreen.classList.remove('hidden');
    elements.messages.innerHTML = '';
    elements.chatTitle.textContent = 'Fast Learning';
    renderConversations();
}

async function deleteConversation(sessionId) {
    if (!confirm('Delete this conversation?')) return;
    
    try {
        await fetch(`${API_URL}/api/conversations/${sessionId}`, {
            method: 'DELETE'
        });
        
        if (sessionId === currentSessionId) {
            createNewChat();
        }
        
        await loadConversations();
    } catch (error) {
        console.error('Error deleting conversation:', error);
    }
}

async function clearAllConversations() {
    if (!confirm('Clear all conversations? This cannot be undone.')) return;
    
    try {
        await fetch(`${API_URL}/api/conversations/clear`, {
            method: 'POST'
        });
        
        createNewChat();
        await loadConversations();
    } catch (error) {
        console.error('Error clearing conversations:', error);
    }
}

// Message Handling
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    
    if (!message || isStreaming) return;
    
    // Hide welcome screen
    elements.welcomeScreen.classList.add('hidden');
    
    // Display user message
    displayMessage('user', message);
    
    // Clear input
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    
    // Disable send button
    elements.sendBtn.disabled = true;
    isStreaming = true;
    
    try {
        // Send via WebSocket for streaming
        socket.emit('send_message', {
            message: message,
            session_id: currentSessionId,
            model: currentModel
        });
        
        // Create AI message container
        createAIMessageContainer();
        
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message. Please try again.');
        hideTypingIndicator();
        isStreaming = false;
    } finally {
        elements.sendBtn.disabled = false;
    }
    
    // Reload conversations to update sidebar
    setTimeout(() => loadConversations(), 1000);
}

function displayMessage(role, content, animate = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (animate) {
        messageDiv.style.opacity = '0';
    }
    
    const avatar = role === 'user' 
        ? '<i class="fas fa-user"></i>' 
        : '<i class="fas fa-robot"></i>';
    
    const roleName = role === 'user' ? 'You' : 'AI Assistant';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-role">${roleName}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${formatMessage(content)}</div>
        </div>
    `;
    
    elements.messages.appendChild(messageDiv);
    
    if (animate) {
        setTimeout(() => {
            messageDiv.style.opacity = '1';
        }, 10);
    }
    
    scrollToBottom();
}

function createAIMessageContainer() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai';
    messageDiv.id = 'streaming-message';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-role">AI Assistant</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text" id="streaming-text"></div>
        </div>
    `;
    
    elements.messages.appendChild(messageDiv);
    scrollToBottom();
}

function appendMessageChunk(chunk) {
    const streamingText = document.getElementById('streaming-text');
    if (streamingText) {
        const currentText = streamingText.textContent || '';
        streamingText.innerHTML = formatMessage(currentText + chunk);
        scrollToBottom();
    }
}

function formatMessage(text) {
    // Use marked.js for proper markdown rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,  // Convert \n to <br>
            gfm: true,     // GitHub Flavored Markdown
            sanitize: false // Allow HTML
        });
        return marked.parse(text);
    }
    
    // Fallback: Basic markdown-like formatting
    let formatted = text;
    
    // Code blocks
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang || 'plaintext'}">${escapeHtml(code.trim())}</code></pre>`;
    });
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic  
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Line breaks - convert double newlines to paragraphs, single to <br>
    formatted = formatted.replace(/\n\n+/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    formatted = '<p>' + formatted + '</p>';
    
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showTypingIndicator() {
    elements.typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    elements.typingIndicator.style.display = 'none';
    
    // Remove streaming message ID
    const streamingMsg = document.getElementById('streaming-message');
    if (streamingMsg) {
        streamingMsg.removeAttribute('id');
    }
    
    const streamingText = document.getElementById('streaming-text');
    if (streamingText) {
        streamingText.removeAttribute('id');
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message ai';
    errorDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-exclamation-circle"></i></div>
        <div class="message-content">
            <div class="message-text" style="color: #ff3b30;">
                <strong>Error:</strong> ${message}
            </div>
        </div>
    `;
    elements.messages.appendChild(errorDiv);
    scrollToBottom();
}

function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function updateModelBadge() {
    const modelNames = {
        'gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'gpt-4': 'GPT-4',
        'local-llama': 'Local LLaMA',
        'local-mistral': 'Local Mistral'
    };
    elements.modelBadge.textContent = modelNames[currentModel] || currentModel;
}

// Utility Functions
function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
