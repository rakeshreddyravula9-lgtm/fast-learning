// API Base URL
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginFormElement = document.getElementById('loginFormElement');
const registerFormElement = document.getElementById('registerFormElement');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const loginError = document.getElementById('loginError');
const registerError = document.getElementById('registerError');
const registerSuccess = document.getElementById('registerSuccess');

// Switch between login and register forms
showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    clearMessages();
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.style.display = 'none';
    loginForm.style.display = 'block';
    clearMessages();
});

// Clear error/success messages
function clearMessages() {
    loginError.style.display = 'none';
    registerError.style.display = 'none';
    registerSuccess.style.display = 'none';
}

// Show error message
function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

// Show success message
function showSuccess(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

// Login form submission
loginFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();
    
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe').checked;
    
    if (!username || !password) {
        showError(loginError, 'Please fill in all fields');
        return;
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store session token
            if (rememberMe) {
                localStorage.setItem('session_token', data.session_token);
            } else {
                sessionStorage.setItem('session_token', data.session_token);
            }
            
            // Store user data
            localStorage.setItem('user_data', JSON.stringify({
                user_id: data.user_id,
                username: data.username,
                email: data.email,
                full_name: data.full_name
            }));
            
            // Redirect to main app
            window.location.href = '/app';
        } else {
            showError(loginError, data.error || 'Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError(loginError, 'Connection error. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
});

// Register form submission
registerFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();
    
    const fullName = document.getElementById('registerFullName').value.trim();
    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    const agreeTerms = document.getElementById('agreeTerms').checked;
    
    // Validation
    if (!username || !email || !password) {
        showError(registerError, 'Please fill in all required fields');
        return;
    }
    
    if (username.length < 3) {
        showError(registerError, 'Username must be at least 3 characters');
        return;
    }
    
    if (password.length < 6) {
        showError(registerError, 'Password must be at least 6 characters');
        return;
    }
    
    if (password !== confirmPassword) {
        showError(registerError, 'Passwords do not match');
        return;
    }
    
    if (!agreeTerms) {
        showError(registerError, 'Please agree to the Terms of Service');
        return;
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                full_name: fullName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(registerSuccess, 'Account created successfully! Redirecting to login...');
            registerFormElement.reset();
            
            // Auto-switch to login after 2 seconds
            setTimeout(() => {
                registerForm.style.display = 'none';
                loginForm.style.display = 'block';
                document.getElementById('loginUsername').value = username;
                clearMessages();
            }, 2000);
        } else {
            showError(registerError, data.error || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError(registerError, 'Connection error. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
    }
});

// Check if user is already logged in
window.addEventListener('DOMContentLoaded', () => {
    const sessionToken = localStorage.getItem('session_token') || sessionStorage.getItem('session_token');
    
    if (sessionToken) {
        // Verify session
        fetch(`${API_URL}/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_token: sessionToken })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Already logged in, redirect to main app
                window.location.href = '/app';
            }
        })
        .catch(error => {
            console.error('Session verification error:', error);
        });
    }
});
