class HealthcareChatbot {
    constructor() {
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearHistoryBtn = document.getElementById('clearHistoryBtn');
        
        this.initializeEventListeners();
        this.loadChatHistory();
    }
    
    initializeEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        
        // Auto-resize textarea and enable send on Enter
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });
        
        // Auto-focus on input
        this.messageInput.focus();
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.toggleSendButton(false);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await this.sendMessage(message);
            this.hideTypingIndicator();
            this.addMessage(response.response, 'bot');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot', true);
            console.error('Error:', error);
        }
        
        this.toggleSendButton(true);
        this.messageInput.focus();
    }
    
    async sendMessage(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-user-md"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        if (isError) {
            messageContent.style.background = '#ffebee';
            messageContent.style.color = '#c62828';
        }
        
        const messageText = document.createElement('p');
        messageText.textContent = content;
        
        const messageInfo = document.createElement('div');
        messageInfo.className = 'message-info';
        
        const messageTime = document.createElement('span');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());
        
        messageInfo.appendChild(messageTime);
        messageContent.appendChild(messageText);
        messageContent.appendChild(messageInfo);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    toggleSendButton(enabled) {
        this.sendBtn.disabled = !enabled;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch('/history');
            if (response.ok) {
                const history = await response.json();
                
                // Clear existing messages except welcome message
                const welcomeMessage = this.chatMessages.querySelector('.message');
                this.chatMessages.innerHTML = '';
                this.chatMessages.appendChild(welcomeMessage);
                
                // Add history messages
                history.forEach(item => {
                    this.addMessage(item.user, 'user');
                    this.addMessage(item.bot, 'bot');
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async clearHistory() {
        if (confirm('Are you sure you want to clear all chat history?')) {
            try {
                const response = await fetch('/history', {
                    method: 'DELETE',
                });
                
                if (response.ok) {
                    // Clear messages except welcome message
                    const welcomeMessage = this.chatMessages.querySelector('.message');
                    this.chatMessages.innerHTML = '';
                    this.chatMessages.appendChild(welcomeMessage);
                    
                    // Show success message
                    this.addMessage('Chat history cleared successfully!', 'bot');
                }
            } catch (error) {
                console.error('Error clearing history:', error);
                this.addMessage('Failed to clear history. Please try again.', 'bot', true);
            }
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HealthcareChatbot();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Additional utility functions
function sanitizeInput(input) {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
}

// Error handling for network issues
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
});