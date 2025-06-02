// Enhanced Support Chat JavaScript
let currentTicketId = null;
let selectedCategory = null;
let currentUser = null;
let chatState = 'welcome'; // welcome, category, issues, form, chat
let messageRefreshInterval = null;

// Offline mode functionality
let isOfflineMode = false;
let offlineTickets = [];

// Debug mode
let debugMode = true; // Set to true for detailed logging
let errorLog = [];

// Enhanced error logging
function logError(context, error, data = null) {
    const errorEntry = {
        timestamp: new Date().toISOString(),
        context: context,
        error: error.toString(),
        stack: error.stack,
        data: data
    };

    errorLog.push(errorEntry);

    if (debugMode) {
        console.group(`🚨 Error in ${context}`);
        console.error('Error:', error);
        if (data) console.log('Data:', data);
        console.groupEnd();
    }

    // Store errors in localStorage for debugging
    try {
        localStorage.setItem('chatErrorLog', JSON.stringify(errorLog));
    } catch (e) {
        console.warn('Could not save error log to localStorage');
    }
}

// Debug function to show system status
function showSystemStatus() {
    console.group('🔍 System Status');
    console.log('Chat State:', chatState);
    console.log('Selected Category:', selectedCategory);
    console.log('Current User:', currentUser);
    console.log('Current Ticket ID:', currentTicketId);
    console.log('Is Offline Mode:', isOfflineMode);
    console.log('Error Log:', errorLog);
    console.groupEnd();
}

// Expose debug functions globally for testing
window.debugChat = {
    showStatus: showSystemStatus,
    errors: errorLog,
    testAPI: testApiConnection,
    clearErrors: () => { errorLog = []; localStorage.removeItem('chatErrorLog'); }
};

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing chat system...');
    loadCategories();
    loadQuickCategories();
    setupEventListeners();

    // Test API connectivity
    testApiConnection();
});

// Setup event listeners
function setupEventListeners() {
    // Rating stars
    document.querySelectorAll('.rating-stars i').forEach(star => {
        star.addEventListener('click', function () {
            const rating = this.dataset.rating;
            setRating(rating);
        });

        star.addEventListener('mouseenter', function () {
            const rating = this.dataset.rating;
            highlightStars(rating);
        });
    });

    // Reset stars on mouse leave
    document.querySelector('.rating-stars')?.addEventListener('mouseleave', () => {
        const activeRating = document.querySelector('.rating-stars i.active:last-of-type')?.dataset.rating || 0;
        highlightStars(activeRating);
    });
}

// Load categories for chat widget
async function loadCategories() {
    try {
        console.log('Loading categories...');
        const response = await fetch('/api/categories');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const categories = await response.json();
        console.log('Categories loaded:', categories);

        const categoriesDiv = document.getElementById('categories');
        if (!categoriesDiv) {
            console.log('Categories div not found');
            return;
        }

        if (Array.isArray(categories) && categories.length > 0) {
            categoriesDiv.innerHTML = categories.map(category => `
                <button class="category-btn" onclick="selectCategory(${category.id}, '${escapeHtml(category.name)}')">
                    <i class="fas fa-${getCategoryIcon(category.name)}"></i>
                    ${category.name}
                </button>
            `).join('');
            console.log('Categories rendered successfully');
        } else {
            console.log('No categories found or invalid format');
            // Use fallback categories
            loadFallbackCategories(categoriesDiv);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        const categoriesDiv = document.getElementById('categories');
        if (categoriesDiv) {
            loadFallbackCategories(categoriesDiv);
        }
    }
}

// Load fallback categories when API fails
function loadFallbackCategories(categoriesDiv) {
    const fallbackCategories = [
        { id: 1, name: 'Payments' },
        { id: 2, name: 'Product Issues' },
        { id: 3, name: 'Technical Glitches' },
        { id: 4, name: 'General Inquiries' }
    ];

    categoriesDiv.innerHTML = fallbackCategories.map(category => `
        <button class="category-btn" onclick="selectCategory(${category.id}, '${escapeHtml(category.name)}')">
            <i class="fas fa-${getCategoryIcon(category.name)}"></i>
            ${category.name}
        </button>
    `).join('') + `
        <div class="text-center mt-3">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                Working in offline mode. Some features may be limited.
            </small>
        </div>
    `;

    console.log('Fallback categories loaded');
}

// Load categories for quick help section
async function loadQuickCategories() {
    try {
        console.log('Loading quick categories...');
        const response = await fetch('/api/categories');

        const quickCategoriesDiv = document.getElementById('quick-categories');
        if (!quickCategoriesDiv) return;

        let categories;

        if (response.ok) {
            categories = await response.json();
        }

        // Use fallback if API failed or returned empty
        if (!categories || !Array.isArray(categories) || categories.length === 0) {
            console.log('Using fallback categories for quick help');
            categories = [
                { id: 1, name: 'Payments' },
                { id: 2, name: 'Product Issues' },
                { id: 3, name: 'Technical Glitches' },
                { id: 4, name: 'General Inquiries' }
            ];
        }

        quickCategoriesDiv.innerHTML = categories.map(category => `
            <div class="col-md-6 col-lg-3">
                <div class="category-card" onclick="openChatWithCategory(${category.id}, '${escapeHtml(category.name)}')">
                    <div class="category-icon">
                        <i class="fas fa-${getCategoryIcon(category.name)}"></i>
                    </div>
                    <h4>${category.name}</h4>
                    <p>Get help with ${category.name.toLowerCase()} related issues</p>
                </div>
            </div>
        `).join('');

        console.log('Quick categories loaded successfully');

    } catch (error) {
        console.error('Error loading quick categories:', error);
        // Load fallback categories even on error
        const quickCategoriesDiv = document.getElementById('quick-categories');
        if (quickCategoriesDiv) {
            const fallbackCategories = [
                { id: 1, name: 'Payments' },
                { id: 2, name: 'Product Issues' },
                { id: 3, name: 'Technical Glitches' },
                { id: 4, name: 'General Inquiries' }
            ];

            quickCategoriesDiv.innerHTML = fallbackCategories.map(category => `
                <div class="col-md-6 col-lg-3">
                    <div class="category-card" onclick="openChatWithCategory(${category.id}, '${escapeHtml(category.name)}')">
                        <div class="category-icon">
                            <i class="fas fa-${getCategoryIcon(category.name)}"></i>
                        </div>
                        <h4>${category.name}</h4>
                        <p>Get help with ${category.name.toLowerCase()} related issues</p>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Get appropriate icon for category
function getCategoryIcon(categoryName) {
    const icons = {
        'Payments': 'credit-card',
        'Product Issues': 'box',
        'Technical Glitches': 'cog',
        'General Inquiries': 'question-circle'
    };
    return icons[categoryName] || 'question-circle';
}

// Open support chat
function openSupportChat() {
    const chatWidget = document.getElementById('chat-widget');
    const fabContainer = document.getElementById('fab-container');

    chatWidget.classList.add('active');
    fabContainer.style.display = 'none';

    // Show welcome screen
    showWelcomeScreen();
}

// Open chat with specific category
function openChatWithCategory(categoryId, categoryName) {
    openSupportChat();
    setTimeout(() => {
        selectCategory(categoryId, categoryName);
    }, 300);
}

// Show welcome screen
function showWelcomeScreen() {
    chatState = 'welcome';
    hideAllChatSections();
    document.getElementById('welcome-screen').style.display = 'block';
}

// Hide all chat sections
function hideAllChatSections() {
    const sections = ['welcome-screen', 'chat-messages', 'common-issues', 'custom-issue-form', 'live-chat'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) element.style.display = 'none';
    });

    const inputs = ['category-input', 'live-chat-input'];
    inputs.forEach(input => {
        const element = document.getElementById(input);
        if (element) element.style.display = 'none';
    });
}

// Handle category selection
async function selectCategory(categoryId, categoryName) {
    selectedCategory = { id: categoryId, name: categoryName };
    chatState = 'issues';

    console.log('Category selected:', selectedCategory);

    try {
        // Load common queries for this category
        const response = await fetch(`/api/common-queries/${categoryId}`);

        hideAllChatSections();

        // Always show the text input for custom questions
        document.getElementById('category-input').style.display = 'block';

        // Update the input placeholder
        const input = document.getElementById('category-message-input');
        input.placeholder = `Type your ${categoryName.toLowerCase()} question here...`;

        let queries = [];

        if (response.ok) {
            queries = await response.json();
            console.log('Common queries loaded:', queries);
        } else {
            console.warn('Failed to load common queries, using fallback');
            queries = getFallbackQueries(categoryName);
        }

        if (queries.length > 0) {
            showCommonIssues(queries);
        } else {
            showNoCommonIssues();
        }

    } catch (error) {
        console.error('Error loading common queries:', error);
        hideAllChatSections();
        document.getElementById('category-input').style.display = 'block';

        // Try to show fallback queries
        const fallbackQueries = getFallbackQueries(categoryName);
        if (fallbackQueries.length > 0) {
            showCommonIssues(fallbackQueries);
        } else {
            showNoCommonIssues();
        }
    }
}

// Get fallback queries for categories
function getFallbackQueries(categoryName) {
    const fallbackQueries = {
        'Payments': [
            { question: 'How do I update my payment method?', solution: 'You can update your payment method in Account Settings > Billing section.' },
            { question: 'Why was my payment declined?', solution: 'Payment declines can happen due to insufficient funds or expired cards. Please check with your bank.' },
            { question: 'How do I get a refund?', solution: 'Refunds can be requested within 30 days. Please contact our billing team.' }
        ],
        'Product Issues': [
            { question: 'The product is not working as expected', solution: 'Please try refreshing the page or clearing your browser cache.' },
            { question: 'I can\'t find a specific feature', solution: 'Check our help documentation or use the search function in the app.' },
            { question: 'How do I report a bug?', solution: 'You can report bugs using the "Report Issue" button or contact support.' }
        ],
        'Technical Glitches': [
            { question: 'The page won\'t load properly', solution: 'Try refreshing the page (Ctrl+F5) or clearing your browser cache.' },
            { question: 'I\'m getting error messages', solution: 'Please note the exact error message and try refreshing the page.' },
            { question: 'The app is running slowly', solution: 'Close other browser tabs and check your internet connection.' }
        ],
        'General Inquiries': [
            { question: 'How do I contact customer support?', solution: 'You can reach us through this chat, email, or phone during business hours.' },
            { question: 'What are your business hours?', solution: 'Our support team is available Monday to Friday, 9 AM to 6 PM EST.' },
            { question: 'How do I create an account?', solution: 'Click "Sign Up" on our homepage and follow the registration steps.' }
        ]
    };

    return fallbackQueries[categoryName] || [];
}

// Show common issues
function showCommonIssues(queries) {
    const commonIssuesDiv = document.getElementById('common-issues');
    const issuesList = document.getElementById('issues-list');

    issuesList.innerHTML = `
        <div class="common-issues-header">
            <h6><i class="fas fa-lightbulb text-warning me-2"></i>Common Issues for ${selectedCategory.name}</h6>
            <p class="text-muted small mb-3">Click on an issue below or type your own question in the box below:</p>
        </div>
        ${queries.map(query => `
            <div class="issue-item" onclick="showSolution('${escapeHtml(query.question)}', '${escapeHtml(query.solution)}')">
                <i class="fas fa-lightbulb text-warning me-2"></i>
                <span>${query.question}</span>
                <i class="fas fa-chevron-right ms-auto text-muted"></i>
            </div>
        `).join('')}
        <div class="custom-input-prompt">
            <div class="divider">
                <span>OR</span>
            </div>
            <p class="text-muted small text-center">
                <i class="fas fa-edit me-1"></i>
                Type your specific question in the text box below
            </p>
        </div>
    `;

    commonIssuesDiv.style.display = 'block';
}

// Show when no common issues are available
function showNoCommonIssues() {
    const commonIssuesDiv = document.getElementById('common-issues');
    const issuesList = document.getElementById('issues-list');

    issuesList.innerHTML = `
        <div class="no-common-issues">
            <div class="text-center p-4">
                <i class="fas fa-edit fa-2x text-primary mb-3"></i>
                <h6>Tell us about your ${selectedCategory.name} issue</h6>
                <p class="text-muted small">
                    Please describe your question or problem in the text box below and we'll help you right away.
                </p>
            </div>
        </div>
    `;

    commonIssuesDiv.style.display = 'block';
}

// Show custom issue form
function showCustomIssueForm() {
    chatState = 'form';
    hideAllChatSections();
    document.getElementById('custom-issue-form').style.display = 'block';
    document.getElementById('category-input').style.display = 'none';
}

// Go back to issues from form
function goBackToIssues() {
    if (selectedCategory) {
        selectCategory(selectedCategory.id, selectedCategory.name);
    } else {
        showWelcomeScreen();
    }
}

// Send category message (from input box)
async function sendCategoryMessage() {
    const input = document.getElementById('category-message-input');
    const message = input.value.trim();

    if (!message) {
        showNotification('Please enter your question or issue.', 'warning');
        return;
    }

    console.log('Sending category message:', message);

    // Show loading state
    const button = input.nextElementSibling;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    try {
        // Ensure selectedCategory is set (fallback to default)
        if (!selectedCategory) {
            console.log('No category selected, using fallback');
            selectedCategory = { id: 1, name: 'General Support' };
        }

        // Create ticket directly with the message
        await createTicketWithMessage(message);
        input.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        showNotification('Failed to send message. Please try again.', 'error');
    } finally {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Add Enter key support for category input
function handleCategoryEnter(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendCategoryMessage();
    }
}

// Submit custom issue
async function submitCustomIssue() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    const description = document.getElementById('issue-description').value.trim();

    if (!description) {
        showNotification('Please describe your issue.', 'warning');
        return;
    }

    console.log('Submitting custom issue:', { name, email, description });

    // Ensure selectedCategory is set (fallback to default)
    if (!selectedCategory) {
        console.log('No category selected, using fallback');
        selectedCategory = { id: 1, name: 'General Support' };
    }

    currentUser = { name, email };
    await createTicketWithMessage(description);
}

// Create ticket with message
async function createTicketWithMessage(message) {
    try {
        if (debugMode) {
            console.group('🎫 Creating Ticket');
            console.log('Message:', message);
            console.log('Selected Category:', selectedCategory);
            console.log('Current User:', currentUser);
        }

        // Ensure we have a valid category (fallback to default)
        const categoryId = selectedCategory?.id || 1;
        const categoryName = selectedCategory?.name || 'General Support';

        const requestBody = {
            name: currentUser?.name || '',
            email: currentUser?.email || '',
            category_id: categoryId,
            subject: `${categoryName} Support Request`,
            message: message
        };

        if (debugMode) {
            console.log('Request Body:', requestBody);
            console.log('Making API call to /api/tickets...');
        }

        const response = await fetch('/api/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (debugMode) {
            console.log('Response Status:', response.status);
            console.log('Response OK:', response.ok);
        }

        if (!response.ok) {
            const errorText = await response.text();
            if (debugMode) {
                console.error('Response Error Text:', errorText);
            }

            // If server is unreachable, switch to offline mode
            if (response.status === 0 || response.status >= 500) {
                console.log('Server unreachable, switching to offline mode');
                createOfflineTicket(message);
                return;
            }

            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();

        if (debugMode) {
            console.log('Response Data:', data);
            console.groupEnd();
        }

        if (data.status === 'success') {
            currentTicketId = data.ticket_id;
            showNotification('Ticket created successfully!', 'success');
            startLiveChat(message);

            // Try to sync any offline tickets
            syncOfflineTickets();
        } else {
            logError('createTicketWithMessage', new Error(`API Error: ${data.message}`), data);
            showNotification(data.message || 'Error creating ticket. Please try again.', 'error');
        }
    } catch (error) {
        if (debugMode) {
            console.groupEnd();
        }

        logError('createTicketWithMessage', error, { message, selectedCategory, currentUser });

        // If it's a network error, switch to offline mode
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            console.log('Network error, switching to offline mode');
            createOfflineTicket(message);
        } else {
            showNotification(`System error: ${error.message}. Please try again later.`, 'error');
        }
    }
}

// Handle offline ticket creation
function createOfflineTicket(message) {
    const ticketId = Date.now(); // Simple ID generation for offline mode
    const ticket = {
        id: ticketId,
        message: message,
        category: selectedCategory?.name || 'General Support',
        name: currentUser?.name || 'Anonymous',
        email: currentUser?.email || '',
        timestamp: new Date().toISOString(),
        status: 'offline-pending'
    };

    // Store in localStorage for persistence
    offlineTickets.push(ticket);
    localStorage.setItem('offlineTickets', JSON.stringify(offlineTickets));

    currentTicketId = ticketId;

    showNotification('Currently offline. Your ticket has been saved and will be sent when connection is restored.', 'info');
    startLiveChat(message);

    // Add offline indicator message
    setTimeout(() => {
        addChatMessage('Thank you for your message. We are currently experiencing connectivity issues, but your ticket has been saved. We will respond as soon as possible.', 'system', new Date().toISOString());
    }, 1000);
}

// Try to sync offline tickets when connection is restored
async function syncOfflineTickets() {
    const savedTickets = localStorage.getItem('offlineTickets');
    if (!savedTickets) return;

    const tickets = JSON.parse(savedTickets);
    const pendingTickets = tickets.filter(t => t.status === 'offline-pending');

    for (const ticket of pendingTickets) {
        try {
            const response = await fetch('/api/tickets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: ticket.name,
                    email: ticket.email,
                    category_id: selectedCategory?.id || 1,
                    subject: `${ticket.category} Support Request`,
                    message: ticket.message
                })
            });

            if (response.ok) {
                // Mark as synced
                ticket.status = 'synced';
                showNotification('Offline ticket has been successfully sent!', 'success');
            }
        } catch (error) {
            console.log('Still offline, will retry later');
            break;
        }
    }

    // Update localStorage
    localStorage.setItem('offlineTickets', JSON.stringify(tickets));
}

// Start live chat
function startLiveChat(initialMessage) {
    chatState = 'chat';
    hideAllChatSections();

    const liveChatDiv = document.getElementById('live-chat');
    liveChatDiv.style.display = 'block';

    document.getElementById('live-chat-input').style.display = 'block';
    document.getElementById('ticket-number').textContent = currentTicketId;

    // Load and display messages
    loadChatMessages();

    // Start auto-refresh for new messages
    startMessageRefresh();

    // Add initial message to chat
    if (initialMessage) {
        addChatMessage(initialMessage, 'user', new Date().toISOString());
    }
}

// Load chat messages
async function loadChatMessages() {
    if (!currentTicketId) return;

    try {
        const response = await fetch(`/api/tickets/${currentTicketId}/messages`);
        const data = await response.json();

        // Check if this is a ticket details response (includes status)
        let messages, ticketStatus;

        if (data.messages && data.status) {
            // This is a full ticket response
            messages = data.messages;
            ticketStatus = data.status;
        } else if (Array.isArray(data)) {
            // This is just messages array
            messages = data;
            // Get ticket status separately
            try {
                const ticketResponse = await fetch(`/api/tickets/${currentTicketId}`);
                if (ticketResponse.ok) {
                    const ticketData = await ticketResponse.json();
                    ticketStatus = ticketData.status;
                }
            } catch (e) {
                console.log('Could not fetch ticket status:', e);
            }
        } else {
            messages = [];
        }

        const messagesContainer = document.getElementById('chat-messages-container');
        messagesContainer.innerHTML = messages.map(msg =>
            createChatMessageHTML(msg.content, msg.is_admin ? 'admin' : 'user', msg.created_at)
        ).join('');

        // Check if ticket has been closed/resolved
        if (ticketStatus && (ticketStatus === 'resolved' || ticketStatus === 'closed')) {
            handleTicketClosure(ticketStatus);
        }

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Error loading chat messages:', error);
    }
}

// Add chat message to UI
function addChatMessage(content, type, timestamp) {
    const messagesContainer = document.getElementById('chat-messages-container');
    const messageHTML = createChatMessageHTML(content, type, timestamp);
    messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Create chat message HTML
function createChatMessageHTML(content, type, timestamp) {
    const avatar = type === 'admin' ? 'A' : 'U';
    const time = formatTime(timestamp);

    return `
        <div class="message ${type}">
            ${content}
            <div class="message-time">${time}</div>
        </div>
    `;
}

// Send message in live chat
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message || !currentTicketId) return;

    try {
        const response = await fetch(`/api/tickets/${currentTicketId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: message,
                user_id: currentUser?.id
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            addChatMessage(message, 'user', new Date().toISOString());
            input.value = '';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showNotification('Error sending message. Please try again.', 'error');
    }
}

// Handle enter key in chat
function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Show solution modal
function showSolution(question, solution) {
    const modal = new bootstrap.Modal(document.getElementById('solutionModal'));
    document.getElementById('solution-content').innerHTML = `
        <div class="solution-content">
            <h6 class="text-primary mb-3">
                <i class="fas fa-question-circle"></i> ${question}
            </h6>
            <div class="solution-text">
                ${solution}
            </div>
        </div>
    `;
    modal.show();
}

// Mark as solved
function markAsSolved() {
    bootstrap.Modal.getInstance(document.getElementById('solutionModal')).hide();

    setTimeout(() => {
        const feedbackModal = new bootstrap.Modal(document.getElementById('feedbackModal'));
        feedbackModal.show();
    }, 300);
}

// Need more help
function needMoreHelp() {
    bootstrap.Modal.getInstance(document.getElementById('solutionModal')).hide();
    showCustomIssueForm();
}

// Toggle chat widget
function toggleChat() {
    const widget = document.getElementById('chat-widget');
    const minimizeBtn = document.querySelector('.minimize-btn i');
    const fabContainer = document.getElementById('fab-container');

    widget.classList.toggle('minimized');

    if (widget.classList.contains('minimized')) {
        minimizeBtn.className = 'fas fa-plus';
        stopMessageRefresh();
    } else {
        minimizeBtn.className = 'fas fa-minus';
        if (chatState === 'chat') {
            startMessageRefresh();
        }
    }
}

// Close chat completely
function closeChat() {
    const widget = document.getElementById('chat-widget');
    const fabContainer = document.getElementById('fab-container');

    widget.classList.remove('active');
    fabContainer.style.display = 'block';

    stopMessageRefresh();
    resetChatState();
}

// Reset chat state
function resetChatState() {
    currentTicketId = null;
    selectedCategory = null;
    currentUser = null;
    chatState = 'welcome';

    // Clear forms
    document.getElementById('user-name').value = '';
    document.getElementById('user-email').value = '';
    document.getElementById('issue-description').value = '';
    document.getElementById('category-message-input').value = '';
    document.getElementById('message-input').value = '';
}

// Start message refresh interval
function startMessageRefresh() {
    if (messageRefreshInterval) return;

    messageRefreshInterval = setInterval(() => {
        if (chatState === 'chat' && currentTicketId) {
            loadChatMessages();
        }
    }, 5000); // Refresh every 5 seconds
}

// Stop message refresh interval
function stopMessageRefresh() {
    if (messageRefreshInterval) {
        clearInterval(messageRefreshInterval);
        messageRefreshInterval = null;
    }
}

// Rating functions
function setRating(rating) {
    document.querySelectorAll('.rating-stars i').forEach((star, index) => {
        star.classList.toggle('active', index < rating);
    });
}

function highlightStars(rating) {
    document.querySelectorAll('.rating-stars i').forEach((star, index) => {
        star.style.color = index < rating ? '#ffc107' : '#ddd';
    });
}

// Submit feedback
async function submitFeedback() {
    const rating = document.querySelectorAll('.rating-stars i.active').length;
    const feedback = document.getElementById('feedback-text').value.trim();

    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticket_id: currentTicketId,
                rating: rating,
                feedback: feedback
            })
        });

        if (response.ok) {
            showNotification('Thank you for your feedback!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
        }
    } catch (error) {
        console.error('Error submitting feedback:', error);
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Add CSS for slideOutRight animation
if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// Utility functions
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopMessageRefresh();
});

// Auto-show FAB after page load
window.addEventListener('load', () => {
    setTimeout(() => {
        const fabContainer = document.getElementById('fab-container');
        if (fabContainer) {
            fabContainer.style.display = 'block';
        }
    }, 2000);
});

// Submit new ticket
async function submitTicket() {
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    const message = document.getElementById('ticket-message').value.trim();

    if (!message) {
        addMessage('Please describe your issue.', 'system');
        return;
    }

    try {
        const response = await fetch('/api/tickets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                email,
                category_id: selectedCategory.id,
                subject: `${selectedCategory.name} Support Request`,
                message
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            currentTicketId = data.ticket_id;
            document.getElementById('chat-input').style.display = 'flex';
            addMessage('Thank you! We have created a ticket for your issue. Our support team will respond shortly.', 'system');
            addMessage(message, 'user');
        } else {
            addMessage('Error creating ticket. Please try again.', 'system');
        }
    } catch (error) {
        console.error('Error submitting ticket:', error);
        addMessage('System error. Please try again later.', 'system');
    }
}

// Send a new message
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) return;

    if (!currentTicketId) {
        addMessage('Please start a new ticket first.', 'system');
        return;
    }

    try {
        const response = await fetch(`/api/tickets/${currentTicketId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: message,
                user_id: currentUser?.id
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            addMessage(message, 'user');
            input.value = '';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Error sending message. Please try again.', 'system');
    }
}

// Toggle chat widget
function toggleChat() {
    const widget = document.getElementById('chat-widget');
    widget.classList.toggle('minimized');

    const minimizeBtn = document.querySelector('.minimize-btn');
    minimizeBtn.textContent = widget.classList.contains('minimized') ? '+' : '−';
}

// Helper function to add a message to the chat
function addMessage(content, type = 'system') {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        ${content}
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Helper function to add HTML content to messages
function addHTML(html) {
    const messagesDiv = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.innerHTML = html;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Event listener for Enter key in message input
document.getElementById('message-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Test API connectivity
async function testApiConnection() {
    try {
        if (debugMode) {
            console.group('🔌 Testing API Connection');
        }

        console.log('Testing API connection...');
        const response = await fetch('/api/health');

        if (response.ok) {
            const data = await response.json();
            if (debugMode) {
                console.log('✅ API connection successful:', data);
                console.groupEnd();
            }
            return true;
        } else {
            if (debugMode) {
                console.warn('❌ API health check failed:', response.status);
                console.groupEnd();
            }

            // Test categories endpoint as fallback
            try {
                const categoriesResponse = await fetch('/api/categories');
                if (categoriesResponse.ok) {
                    console.log('Categories endpoint working, health endpoint may be down');
                    return true;
                }
            } catch (e) {
                console.warn('Both health and categories endpoints failed');
            }

            showNotification('Support system is experiencing issues. Some features may be limited.', 'warning');
            return false;
        }
    } catch (error) {
        if (debugMode) {
            console.groupEnd();
        }

        logError('testApiConnection', error);
        console.error('API connection test failed:', error);
        showNotification('Unable to connect to support system. You can still submit tickets which will be sent when connection is restored.', 'info');
        return false;
    }
}

// Handle ticket closure/resolution
function handleTicketClosure(status) {
    // Only show closure handling once
    if (chatState === 'closed') return;

    console.log(`Ticket ${currentTicketId} has been ${status}`);

    // Update chat state
    chatState = 'closed';

    // Disable chat input
    const messageInput = document.getElementById('message-input');
    const sendButton = document.querySelector('#live-chat-input button');

    if (messageInput) {
        messageInput.disabled = true;
        messageInput.placeholder = `This conversation has been ${status}`;
    }

    if (sendButton) {
        sendButton.disabled = true;
        sendButton.innerHTML = '<i class="fas fa-check"></i>';
    }

    // Update chat status indicator
    const statusIndicator = document.querySelector('.chat-status .status-indicator');
    if (statusIndicator) {
        statusIndicator.innerHTML = `
            <i class="fas fa-check-circle text-success"></i>
            <span>${status === 'resolved' ? 'Issue Resolved' : 'Chat Closed'}</span>
        `;
    }

    // Stop message refresh since ticket is closed
    stopMessageRefresh();

    // Show notification
    const statusMessage = status === 'resolved'
        ? 'Your issue has been resolved! Thank you for contacting support.'
        : 'This conversation has been closed.';

    showNotification(statusMessage, 'success');

    // Show feedback modal after a brief delay
    setTimeout(() => {
        showFeedbackModal();
    }, 2000);
}

// Show feedback modal
function showFeedbackModal() {
    // Create feedback modal if it doesn't exist
    let feedbackModal = document.getElementById('feedbackModal');

    if (!feedbackModal) {
        feedbackModal = document.createElement('div');
        feedbackModal.className = 'modal fade';
        feedbackModal.id = 'feedbackModal';
        feedbackModal.setAttribute('tabindex', '-1');
        feedbackModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-star text-warning me-2"></i>
                            How was your experience?
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center mb-4">
                            <p class="text-muted">Please rate your support experience</p>
                            <div class="rating-stars">
                                <i class="fas fa-star" data-rating="1"></i>
                                <i class="fas fa-star" data-rating="2"></i>
                                <i class="fas fa-star" data-rating="3"></i>
                                <i class="fas fa-star" data-rating="4"></i>
                                <i class="fas fa-star" data-rating="5"></i>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="feedback-text" class="form-label">Additional feedback (optional)</label>
                            <textarea class="form-control" id="feedback-text" rows="3" 
                                placeholder="Tell us about your experience..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Skip</button>
                        <button type="button" class="btn btn-primary" onclick="submitFeedback()">Submit Feedback</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(feedbackModal);

        // Add event listeners for rating stars
        feedbackModal.querySelectorAll('.rating-stars i').forEach(star => {
            star.addEventListener('click', function () {
                const rating = this.dataset.rating;
                setRating(rating);
            });

            star.addEventListener('mouseenter', function () {
                const rating = this.dataset.rating;
                highlightStars(rating);
            });
        });

        // Reset stars on mouse leave
        feedbackModal.querySelector('.rating-stars').addEventListener('mouseleave', () => {
            const activeRating = feedbackModal.querySelector('.rating-stars i.active:last-of-type')?.dataset.rating || 0;
            highlightStars(activeRating);
        });
    }

    // Show the modal
    const bootstrapModal = new bootstrap.Modal(feedbackModal);
    bootstrapModal.show();
}
