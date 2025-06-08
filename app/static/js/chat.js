// Chat functionality for YouCloudPay Devshop Support
class ChatInterface {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.chatContainer = document.getElementById('chat-container');
        this.messagesContainer = document.getElementById('messages-container');
        this.chatForm = document.getElementById('chat-form');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator-message');
        this.fileInput = document.getElementById('file-input');
        this.filePreview = document.getElementById('file-preview');
        this.fileName = document.getElementById('file-name');
        this.selectedFile = null;
        this.conversationId = null;

        this.initializeChat();
        this.setupEventListeners();
    }

    initializeChat() {
        // Auto-resize textarea
        this.messageInput.addEventListener('input', this.autoResizeTextarea.bind(this));

        // Create new conversation
        this.createConversation();

        // Load chat history if conversation exists
        this.loadChatHistory();
    }

    setupEventListeners() {
        // Form submission
        this.chatForm.addEventListener('submit', this.sendMessage.bind(this));

        // Enter key to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage(e);
            }
        });

        // Language change
        const languageSelector = document.getElementById('language-selector');
        if (languageSelector) {
            languageSelector.addEventListener('change', this.changeLanguage.bind(this));
        }

        // File input
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
    }

    async createConversation() {
        try {
            const response = await fetch('/api/chat/conversations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            if (response.ok) {
                const data = await response.json();
                this.conversationId = data.conversation_id;
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    }

    async loadChatHistory() {
        if (!this.conversationId) return;

        try {
            const response = await fetch(`/api/chat/conversations/${this.conversationId}/messages`);
            if (response.ok) {
                const data = await response.json();
                data.messages.forEach(message => {
                    this.displayMessage(message.content, message.is_bot, message.created_at, message.attachments);
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    async sendMessage(e) {
        e.preventDefault();

        const message = this.messageInput.value.trim();
        if (!message && !this.selectedFile) return;

        // Disable input while sending
        this.setInputState(false);

        // Display user message
        if (message) {
            this.displayMessage(message, false);
        }

        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const formData = new FormData();
            formData.append('message', message);
            formData.append('conversation_id', this.conversationId);

            if (this.selectedFile) {
                formData.append('file', this.selectedFile);
                this.removeFile();
            }

            const response = await fetch('/api/chat/send', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();

                // Hide typing indicator
                this.hideTypingIndicator();

                // Display bot response
                this.displayMessage(data.response, true, null, data.attachments);

                // Handle suggestions
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.displayMessage('Sorry, I encountered an error. Please try again.', true);
        } finally {
            this.setInputState(true);
            this.messageInput.focus();
        }
    }

    displayMessage(content, isBot, timestamp = null, attachments = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-3';

        const avatarClass = isBot ? 'bg-blue-600' : 'bg-gray-600';
        const avatarIcon = isBot ?
            `<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>` :
            `<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>`;

        const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
        const senderName = isBot ? 'Support Assistant' : 'You';

        let attachmentHtml = '';
        if (attachments && attachments.length > 0) {
            attachmentHtml = attachments.map(att => {
                if (att.file_type.startsWith('image/')) {
                    return `<img src="${att.file_path}" alt="${att.filename}" class="max-w-xs rounded-lg mt-2">`;
                } else {
                    return `<div class="flex items-center space-x-2 mt-2 p-2 bg-gray-50 rounded border">
                        <svg class="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                        </svg>
                        <a href="${att.file_path}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm">${att.filename}</a>
                    </div>`;
                }
            }).join('');
        }

        messageDiv.innerHTML = `
            <div class="flex-shrink-0">
                <div class="h-8 w-8 ${avatarClass} rounded-full flex items-center justify-center">
                    ${avatarIcon}
                </div>
            </div>
            <div class="flex-1 min-w-0">
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                    <p class="text-sm text-gray-900">${this.formatMessage(content)}</p>
                    ${attachmentHtml}
                </div>
                <div class="mt-1 text-xs text-gray-500">
                    ${senderName} • ${timeStr}
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" class="text-blue-600 hover:text-blue-800">$1</a>');

        // Convert line breaks to <br>
        content = content.replace(/\n/g, '<br>');

        return content;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    showSuggestions(suggestions) {
        const suggestionsDiv = document.getElementById('suggestions');
        suggestionsDiv.innerHTML = '';

        suggestions.forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 hover:bg-gray-200';
            button.textContent = suggestion;
            button.onclick = () => this.sendSuggestion(suggestion);
            suggestionsDiv.appendChild(button);
        });

        suggestionsDiv.style.display = 'flex';
    }

    sendSuggestion(suggestion) {
        this.messageInput.value = suggestion;
        this.sendMessage({ preventDefault: () => { } });
        document.getElementById('suggestions').style.display = 'none';
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        this.fileInput.disabled = !enabled;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 100);
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }

        this.selectedFile = file;
        this.fileName.textContent = file.name;
        this.filePreview.classList.remove('hidden');
    }

    removeFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.filePreview.classList.add('hidden');
    }

    async changeLanguage(event) {
        const language = event.target.value;

        try {
            const response = await fetch('/api/set-language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ language })
            });

            if (response.ok) {
                // Reload page to apply new language
                window.location.reload();
            }
        } catch (error) {
            console.error('Error changing language:', error);
        }
    }

    async exportChat() {
        if (!this.conversationId) return;

        try {
            const response = await fetch(`/api/chat/conversations/${this.conversationId}/export`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `chat-export-${new Date().toISOString().split('T')[0]}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Error exporting chat:', error);
        }
    }

    clearChat() {
        if (confirm('Are you sure you want to clear this chat? This action cannot be undone.')) {
            this.messagesContainer.innerHTML = '';
            this.createConversation();
        }
    }

    startComplaint() {
        const messages = Array.from(this.messagesContainer.children)
            .map(msg => msg.querySelector('.text-sm').textContent)
            .join('\n\n');

        // Open complaint form with chat context
        const url = `/complaints/new?context=${encodeURIComponent(messages)}`;
        window.open(url, '_blank');
    }
}

// Utility functions for global use
function sendQuickMessage(message) {
    if (window.chatInterface) {
        window.chatInterface.messageInput.value = message;
        window.chatInterface.sendMessage({ preventDefault: () => { } });
    }
}

function toggleEmojiPicker() {
    const picker = document.getElementById('emoji-picker');
    picker.classList.toggle('hidden');
}

function insertEmoji(emoji) {
    const input = document.getElementById('message-input');
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;

    input.value = text.substring(0, start) + emoji + text.substring(end);
    input.selectionStart = input.selectionEnd = start + emoji.length;
    input.focus();

    toggleEmojiPicker();
}

function toggleChatMenu() {
    const menu = document.getElementById('chat-menu');
    menu.classList.toggle('hidden');
}

function exportChat() {
    if (window.chatInterface) {
        window.chatInterface.exportChat();
    }
    toggleChatMenu();
}

function clearChat() {
    if (window.chatInterface) {
        window.chatInterface.clearChat();
    }
    toggleChatMenu();
}

function startComplaint() {
    if (window.chatInterface) {
        window.chatInterface.startComplaint();
    }
    toggleChatMenu();
}

function handleFileSelect(event) {
    if (window.chatInterface) {
        window.chatInterface.handleFileSelect(event);
    }
}

function removeFile() {
    if (window.chatInterface) {
        window.chatInterface.removeFile();
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    window.chatInterface = new ChatInterface();

    // Close emoji picker when clicking outside
    document.addEventListener('click', function (event) {
        const picker = document.getElementById('emoji-picker');
        const emojiButton = event.target.closest('[onclick="toggleEmojiPicker()"]');

        if (!picker.contains(event.target) && !emojiButton) {
            picker.classList.add('hidden');
        }
    });
});

// Connection status indicator
function updateConnectionStatus(isConnected) {
    const statusDot = document.getElementById('connection-status');
    const statusText = statusDot.nextElementSibling;

    if (isConnected) {
        statusDot.className = 'h-2 w-2 bg-green-400 rounded-full';
        statusText.textContent = 'Connected';
    } else {
        statusDot.className = 'h-2 w-2 bg-red-400 rounded-full';
        statusText.textContent = 'Disconnected';
    }
}

// Simulate connection monitoring
setInterval(() => {
    fetch('/api/health')
        .then(response => updateConnectionStatus(response.ok))
        .catch(() => updateConnectionStatus(false));
}, 30000); // Check every 30 seconds
