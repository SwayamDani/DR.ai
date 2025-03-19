/**
 * Dr.ai - AI Health Assistant
 * Main JavaScript file for handling chat functionality (Tailwind CSS version)
 */

// Create a namespace for the application
const draiApp = (function() {
    // DOM elements
    let sidebar;
    let chatbox;
    let messagesContainer;
    let messages;
    let userInput;
    let sendButton;
    let promptRow;
    let chatHistory;
    let toggleButton;
    let overlay;
    let loadingIndicator;
    
    // Current thread ID for API calls
    let currentThreadId = null;
    
    /**
     * Initialize the application
     */
    function init() {
        // Get DOM elements
        sidebar = document.getElementById('sidebar');
        chatbox = document.getElementById('chatbox');
        messagesContainer = document.getElementById('messages-container');
        messages = document.getElementById('messages');
        userInput = document.getElementById('user_input');
        sendButton = document.getElementById('send-button');
        promptRow = document.querySelector('.prompt-row');
        chatHistory = document.getElementById('chat-history');
        toggleButton = document.getElementById('toggle-sidebar');
        overlay = document.getElementById('overlay');
        loadingIndicator = document.getElementById('loading');
        
        // Setup event listeners
        setupEventListeners();
        
        // Initialize chat UI
        createTimestamp();
        setupPromptButtons();
        setupMobileUI();
        
        // Focus on input field
        userInput.focus();
        
        // Create a new thread for the conversation
        createNewThread();
    }
    
    /**
     * Setup all event listeners
     */
    function setupEventListeners() {
        // Send message on Enter key
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Send message on button click
        sendButton.addEventListener('click', sendMessage);
        
        // Mobile sidebar toggle
        toggleButton.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-open');
            overlay.classList.toggle('active');
        });
        
        // Close sidebar when clicking overlay
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('sidebar-open');
            overlay.classList.remove('active');
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('sidebar-open');
                overlay.classList.remove('active');
            }
            setupMobileUI();
        });
        
        // Setup history item listeners
        setupHistoryItemListeners();
    }
    
    /**
     * Setup mobile UI elements
     */
    function setupMobileUI() {
        const isMobile = window.innerWidth <= 768;
        // Show toggle button on mobile
        toggleButton.style.display = isMobile ? 'flex' : 'none';
    }
    
    /**
     * Create a timestamp element
     */
    function createTimestamp() {
        const timestamp = document.createElement('div');
        timestamp.className = 'text-white/50 text-sm text-center my-4 font-medium';
        const now = new Date();
        timestamp.textContent = now.toLocaleString('en-US', { 
            weekday: 'short',
            month: 'short', 
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });
        
        if (messages.firstChild) {
            messages.insertBefore(timestamp, messages.firstChild);
        } else {
            messages.appendChild(timestamp);
        }
    }
    
    /**
     * Setup prompt button click listeners
     */
    function setupPromptButtons() {
        document.querySelectorAll('.prompt-button').forEach(button => {
            button.addEventListener('click', function() {
                const promptText = this.getAttribute('data-prompt') || this.textContent;
                sendPrompt(promptText);
                
                // Close sidebar on mobile
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('sidebar-open');
                    overlay.classList.remove('active');
                }
            });
        });
    }
    
    /**
     * Setup event listeners for chat history items
     */
    function setupHistoryItemListeners() {
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', function() {
                // In a real implementation, this would load the selected chat
                // For now, we'll just toggle the sidebar on mobile
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('sidebar-open');
                    overlay.classList.remove('active');
                }
            });
        });
    }
    
    /**
     * Create a new thread for the conversation
     */
    function createNewThread() {
        fetch('/new_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentThreadId = data.thread_id;
            } else {
                throw new Error('Failed to create new chat');
            }
        })
        .catch(error => {
            console.error('Error creating new thread:', error);
            messages.innerHTML += `
                <div class="message assistant error rounded-2xl p-5 bg-red-500/10 border border-red-500/30 text-white/90 mr-auto animate-fade-in"><strong>Error:</strong> Failed to start new chat</div>
            `;
        });
    }
    
    /**
     * Send a message to the AI
     */
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;  // Prevent sending empty messages
        
        // Append user message to chatbox
        messages.innerHTML += `<div class="message user rounded-2xl p-5 bg-gradient text-white ml-auto rounded-br-sm animate-fade-in max-w-[85%] break-words"><strong>You:</strong> ${message}</div>`;
        showLoading();
        scrollToBottom();
        
        // Clear input field
        userInput.value = '';
        
        // Send message to server
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message,
                requestPrompts: true 
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            // Append assistant's response to chatbox
            messages.innerHTML += `<div class="message assistant rounded-2xl p-5 bg-message-bg text-white mr-auto rounded-bl-sm border border-white/10 animate-fade-in max-w-[85%] break-words"><strong>Dr.ai:</strong> ${data.response}</div>`;
            
            // Update prompt suggestions
            if (data.relatedPrompts && data.relatedPrompts.length > 0) {
                updatePromptButtons(data.relatedPrompts);
            }
            
            // Scroll to bottom
            scrollToBottom();
            
            // Update first history item title if it's "New conversation"
            const firstHistoryItem = document.querySelector('.history-item .history-title');
            if (firstHistoryItem && firstHistoryItem.textContent === 'New conversation') {
                firstHistoryItem.textContent = message.length > 25 ? message.substring(0, 22) + '...' : message;
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            hideLoading();
            messages.innerHTML += `<div class="message assistant error rounded-2xl p-5 bg-red-500/10 border border-red-500/30 text-white/90 mr-auto animate-fade-in"><strong>Error:</strong> Failed to send message</div>`;
            scrollToBottom();
        });
    }
    
    /**
     * Send a predefined prompt
     * @param {string} message - The prompt message
     */
    function sendPrompt(message) {
        // Append user message to chatbox
        messages.innerHTML += `<div class="message user rounded-2xl p-5 bg-gradient text-white ml-auto rounded-br-sm animate-fade-in max-w-[85%] break-words"><strong>You:</strong> ${message}</div>`;
        showLoading();
        scrollToBottom();
        
        // Send prompt to server
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message,
                requestPrompts: true 
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            // Append assistant's response to chatbox
            messages.innerHTML += `<div class="message assistant rounded-2xl p-5 bg-message-bg text-white mr-auto rounded-bl-sm border border-white/10 animate-fade-in max-w-[85%] break-words"><strong>Dr.ai:</strong> ${data.response}</div>`;
            
            // Update prompt suggestions
            if (data.relatedPrompts && data.relatedPrompts.length > 0) {
                updatePromptButtons(data.relatedPrompts);
            }
            
            // Scroll to bottom
            scrollToBottom();
            
            // Update first history item title if it's "New conversation"
            const firstHistoryItem = document.querySelector('.history-item .history-title');
            if (firstHistoryItem && firstHistoryItem.textContent === 'New conversation') {
                firstHistoryItem.textContent = message.length > 25 ? message.substring(0, 22) + '...' : message;
            }
        })
        .catch(error => {
            console.error('Error sending prompt:', error);
            hideLoading();
            messages.innerHTML += `<div class="message assistant error rounded-2xl p-5 bg-red-500/10 border border-red-500/30 text-white/90 mr-auto animate-fade-in"><strong>Error:</strong> Failed to send message</div>`;
            scrollToBottom();
        });
    }
    
    /**
     * Start a new chat conversation
     */
    function startNewChat() {
        // Clear chatbox
        messages.innerHTML = '';
        userInput.value = '';
        
        // Add timestamp for new chat
        createTimestamp();
        
        // Add welcome message
        messages.innerHTML += `
            <div class="message assistant welcome max-w-[90%] rounded-2xl p-5 bg-welcome-bg border border-welcome-border mb-4 animate-fade-in">
                <strong>Dr.ai:</strong> 
                <p>Hello! I'm Dr.ai, your AI health assistant. How can I help you today?</p>
                <div class="mt-4 text-sm p-2 px-3 bg-white/5 rounded-lg text-white/70">Note: I provide general information only. For medical emergencies or specific diagnoses, please consult a healthcare professional.</div>
            </div>
        `;
        
        // Reset prompt buttons to initial state
        promptRow.innerHTML = `
            <button class="prompt-button py-3 px-4 bg-white/5 text-white border border-white/10 rounded-lg font-medium text-sm transition-all duration-200 text-left whitespace-nowrap overflow-hidden text-ellipsis backdrop-blur-sm hover:bg-white/10 hover:-translate-y-0.5 hover:shadow-md" data-prompt="How do I lose weight healthily?">Weight loss tips</button>
            <button class="prompt-button py-3 px-4 bg-white/5 text-white border border-white/10 rounded-lg font-medium text-sm transition-all duration-200 text-left whitespace-nowrap overflow-hidden text-ellipsis backdrop-blur-sm hover:bg-white/10 hover:-translate-y-0.5 hover:shadow-md" data-prompt="What causes migraines?">Migraine causes</button>
            <button class="prompt-button py-3 px-4 bg-white/5 text-white border border-white/10 rounded-lg font-medium text-sm transition-all duration-200 text-left whitespace-nowrap overflow-hidden text-ellipsis backdrop-blur-sm hover:bg-white/10 hover:-translate-y-0.5 hover:shadow-md" data-prompt="Tips for better sleep">Sleep improvement</button>
        `;
        
        // Re-setup prompt buttons
        setupPromptButtons();
        
        // Create new thread
        fetch('/new_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentThreadId = data.thread_id;
                
                // Add to chat history
                addChatToHistory('New conversation');
            } else {
                throw new Error('Failed to create new chat');
            }
        })
        .catch(error => {
            console.error('Error creating new chat:', error);
            messages.innerHTML += `
                <div class="message assistant error rounded-2xl p-5 bg-red-500/10 border border-red-500/30 text-white/90 mr-auto animate-fade-in"><strong>Error:</strong> Failed to start new chat</div>
            `;
        });
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('sidebar-open');
            overlay.classList.remove('active');
        }
    }
    
    /**
     * Add a chat to the history sidebar
     * @param {string} title - Title of the chat
     */
    function addChatToHistory(title) {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', { 
            hour: 'numeric',
            minute: 'numeric',
            hour12: true
        });
        
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item flex justify-between items-center p-3 bg-white/5 rounded-lg text-sm cursor-pointer transition-all duration-200 hover:bg-white/10';
        historyItem.innerHTML = `
            <span class="history-title font-medium whitespace-nowrap overflow-hidden text-ellipsis max-w-[160px]">${title}</span>
            <span class="history-time text-xs text-white/50">${timeString}</span>
        `;
        
        // Add at the beginning (most recent first)
        if (chatHistory.firstChild) {
            chatHistory.insertBefore(historyItem, chatHistory.firstChild);
        } else {
            chatHistory.appendChild(historyItem);
        }
        
        // Limit to 5 history items
        const historyItems = chatHistory.querySelectorAll('.history-item');
        if (historyItems.length > 5) {
            chatHistory.removeChild(historyItems[historyItems.length - 1]);
        }
        
        // Update history item listeners
        setupHistoryItemListeners();
    }
    
    /**
     * Update the prompt buttons with new suggestions
     * @param {Array} relatedPrompts - Array of prompt suggestions
     */
    function updatePromptButtons(relatedPrompts) {
        promptRow.innerHTML = '';
        
        relatedPrompts.forEach(prompt => {
            const button = document.createElement('button');
            button.className = 'prompt-button py-3 px-4 bg-white/5 text-white border border-white/10 rounded-lg font-medium text-sm transition-all duration-200 text-left whitespace-nowrap overflow-hidden text-ellipsis backdrop-blur-sm hover:bg-white/10 hover:-translate-y-0.5 hover:shadow-md';
            button.setAttribute('data-prompt', prompt);
            button.textContent = prompt;
            button.addEventListener('click', function() {
                sendPrompt(prompt);
                
                // Close sidebar on mobile
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('sidebar-open');
                    overlay.classList.remove('active');
                }
            });
            
            promptRow.appendChild(button);
        });
        
        // On mobile, make prompt row vertical
        if (window.innerWidth <= 768) {
            promptRow.classList.add('flex-col');
        } else {
            promptRow.classList.remove('flex-col');
        }
    }
    
    /**
     * Show loading indicator
     */
    function showLoading() {
        loadingIndicator.classList.remove('hidden');
    }
    
    /**
     * Hide loading indicator
     */
    function hideLoading() {
        loadingIndicator.classList.add('hidden');
    }
    
    /**
     * Scroll messages container to bottom
     */
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Initialize the app when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', init);
    
    // Public API
    return {
        sendMessage,
        sendPrompt,
        startNewChat,
        scrollToBottom
    };
})();