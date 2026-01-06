/**
 * AI-Powered Todo Chatbot Frontend
 * Phase III: Conversational Interface
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const JWT_TOKEN_KEY = 'chatbot_jwt_token';
const CONVERSATION_ID_KEY = 'chatbot_conversation_id';

// Get JWT token from localStorage or generate a test one
function getJWTToken() {
    let token = localStorage.getItem(JWT_TOKEN_KEY);
    if (!token) {
        // For local testing: Create a simple JWT with user_id
        token = generateTestJWT('test-user');
        localStorage.setItem(JWT_TOKEN_KEY, token);
    }
    return token;
}

// Generate a simple JWT for testing
function generateTestJWT(userId) {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({ sub: userId, iat: Math.floor(Date.now() / 1000) }));
    const signature = 'test-signature';
    return `${header}.${payload}.${signature}`;
}

// Get current conversation ID
function getConversationId() {
    return localStorage.getItem(CONVERSATION_ID_KEY);
}

// Set conversation ID
function setConversationId(id) {
    localStorage.setItem(CONVERSATION_ID_KEY, id);
}

// Clear conversation
function clearConversation() {
    localStorage.removeItem(CONVERSATION_ID_KEY);
}

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const messageForm = document.getElementById('messageForm');
const messagesContainer = document.getElementById('messagesContainer');
const todosList = document.getElementById('todosList');
const statusText = document.getElementById('statusText');
const loadingOverlay = document.getElementById('loadingOverlay');
const newConvBtn = document.getElementById('newConvBtn');
const refreshBtn = document.getElementById('refreshBtn');
const errorModal = document.getElementById('errorModal');
const closeModal = document.getElementById('closeModal');
const closeErrorBtn = document.getElementById('closeErrorBtn');
const errorMessage = document.getElementById('errorMessage');

// Event Listeners
messageForm.addEventListener('submit', sendMessage);
newConvBtn.addEventListener('click', startNewConversation);
refreshBtn.addEventListener('click', loadTodos);
closeModal.addEventListener('click', () => errorModal.classList.remove('show'));
closeErrorBtn.addEventListener('click', () => errorModal.classList.remove('show'));

// Quick action buttons
document.getElementById('quickCreate').addEventListener('click', () => {
    messageInput.value = 'Create a todo to ';
    messageInput.focus();
});
document.getElementById('quickList').addEventListener('click', () => {
    messageInput.value = 'show todos';
    messageForm.dispatchEvent(new Event('submit'));
});
document.getElementById('quickClear').addEventListener('click', () => {
    messageInput.value = 'delete all completed todos';
    messageForm.dispatchEvent(new Event('submit'));
});

/**
 * Send message to the chatbot
 */
async function sendMessage(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input
    messageInput.value = '';
    messageInput.focus();

    // Disable send button
    sendBtn.disabled = true;

    // Display user message
    displayMessage(message, 'user');

    // Show loading
    setLoading(true);
    setStatus('');

    try {
        // Prepare request
        const conversationId = getConversationId();
        const requestBody = {
            message: message,
            conversation_id: conversationId || null
        };

        // Send request
        const response = await fetch(`${API_BASE_URL}/chat/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getJWTToken()}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();

        // Save conversation ID
        if (data.conversation_id) {
            setConversationId(data.conversation_id);
        }

        // Display assistant message
        displayMessage(data.response, 'assistant');

        // Update todos list
        if (data.todos) {
            displayTodos(data.todos);
        }

        // Log tool calls if any
        if (data.tool_invocations && data.tool_invocations.length > 0) {
            console.log('Tool Invocations:', data.tool_invocations);
            setStatus(`✓ ${data.tool_invocations.length} tool(s) executed`);
        }

    } catch (error) {
        console.error('Error:', error);
        showError(`Failed to send message: ${error.message}`);
        // Display error in chat
        displayMessage(`❌ Error: ${error.message}`, 'assistant');
    } finally {
        setLoading(false);
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

/**
 * Display a message in the chat
 */
function displayMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div>
            <div class="message-bubble">${escapeHtml(text)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;

    // Remove welcome message if first message
    const welcomeMsg = messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Display todos in the sidebar
 */
function displayTodos(todos) {
    if (!todos || todos.length === 0) {
        todosList.innerHTML = '<p class="empty-state">No todos yet</p>';
        return;
    }

    todosList.innerHTML = '';
    todos.forEach(todo => {
        const todoItem = document.createElement('div');
        todoItem.classList.add('todo-item');
        if (todo.status === 'completed') {
            todoItem.classList.add('completed');
        }

        todoItem.innerHTML = `
            <div class="todo-title">${escapeHtml(todo.title)}</div>
            <div class="todo-status">${todo.status}</div>
        `;

        todosList.appendChild(todoItem);
    });
}

/**
 * Load todos (refresh)
 */
async function loadTodos() {
    const conversationId = getConversationId();
    if (!conversationId) {
        setStatus('No active conversation');
        return;
    }

    refreshBtn.style.transform = 'rotate(180deg)';
    setLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getJWTToken()}`
            },
            body: JSON.stringify({
                message: 'Show my todos',
                conversation_id: conversationId
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        if (data.todos) {
            displayTodos(data.todos);
            setStatus('✓ Todos refreshed');
        }
    } catch (error) {
        console.error('Error loading todos:', error);
        showError(`Failed to refresh todos: ${error.message}`);
    } finally {
        setLoading(false);
        refreshBtn.style.transform = '';
    }
}

/**
 * Start a new conversation
 */
function startNewConversation() {
    if (confirm('Start a new conversation? Current conversation will be archived.')) {
        clearConversation();
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <h2>New Conversation Started</h2>
                <p>Say something like:</p>
                <ul>
                    <li>"Create a todo to buy groceries"</li>
                    <li>"Show me all my tasks"</li>
                    <li>"Mark the first todo as done"</li>
                    <li>"Delete the meeting reminder"</li>
                </ul>
            </div>
        `;
        todosList.innerHTML = '<p class="empty-state">No todos yet</p>';
        setStatus('');
        messageInput.focus();
    }
}

/**
 * Show loading indicator
 */
function setLoading(show) {
    if (show) {
        loadingOverlay.classList.add('show');
    } else {
        loadingOverlay.classList.remove('show');
    }
}

/**
 * Show status message
 */
function setStatus(message) {
    statusText.textContent = message;
    statusText.className = 'status-text';
    if (message.includes('Error')) {
        statusText.classList.add('error');
    } else if (message.includes('✓')) {
        statusText.classList.add('success');
    }
}

/**
 * Show error modal
 */
function showError(message) {
    errorMessage.textContent = message;
    errorModal.classList.add('show');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Initialize app
 */
function initializeApp() {
    console.log('Chatbot initialized');
    console.log('JWT Token:', getJWTToken());

    // Load saved conversation if exists
    const conversationId = getConversationId();
    if (conversationId) {
        setStatus('Resuming previous conversation...');
        loadTodos();
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initializeApp);

// Focus on input when page loads
window.addEventListener('load', () => {
    messageInput.focus();
});
