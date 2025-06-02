// Admin Dashboard JavaScript
let currentTicketId = null;
let activeConversations = new Map();
let refreshInterval = null;

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    loadCategories();
    loadTickets();
    loadActiveConversations();

    // Start auto-refresh for live chat
    startAutoRefresh();
});

// Navigation functions
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');

    // Update menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'tickets': 'Tickets',
        'live-chat': 'Live Chat',
        'analytics': 'Analytics'
    };
    document.getElementById('page-title').textContent = titles[sectionName];

    // Load section-specific data
    if (sectionName === 'tickets') {
        loadTickets();
    } else if (sectionName === 'live-chat') {
        loadActiveConversations();
    } else if (sectionName === 'analytics') {
        loadAnalytics();
    }
}

// Dashboard functions
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data...');
        const response = await fetch('/api/admin/dashboard-stats');

        console.log('Dashboard response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Dashboard API error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const stats = await response.json();
        console.log('Dashboard stats received:', stats);

        // Check if response has error
        if (stats.error) {
            console.error('Dashboard stats error:', stats.error);
            showNotification(`Dashboard error: ${stats.error}`, 'error');
            return;
        }

        document.getElementById('total-tickets').textContent = stats.totalTickets || 0;
        document.getElementById('pending-tickets').textContent = stats.pendingTickets || 0;
        document.getElementById('resolved-tickets').textContent = stats.resolvedTickets || 0;
        document.getElementById('active-chats').textContent = stats.activeChats || 0;

        console.log('Dashboard stats updated successfully');
        loadRecentActivity();

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Failed to load dashboard data. Please check the server connection.', 'error');

        // Set fallback values
        document.getElementById('total-tickets').textContent = '?';
        document.getElementById('pending-tickets').textContent = '?';
        document.getElementById('resolved-tickets').textContent = '?';
        document.getElementById('active-chats').textContent = '?';
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/admin/recent-activity');
        const activities = await response.json();

        const activityList = document.getElementById('recent-activity');
        if (activities.length === 0) {
            activityList.innerHTML = '<p class="text-muted">No recent activity</p>';
            return;
        }

        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item fade-in">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <h6>${activity.title}</h6>
                    <p>${activity.description} • ${formatTime(activity.created_at)}</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent activity:', error);
    }
}

// Tickets functions
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();

        const categoryFilter = document.getElementById('category-filter');
        if (categoryFilter) {
            categoryFilter.innerHTML = '<option value="">All Categories</option>' +
                categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadTickets() {
    try {
        console.log('Loading tickets...');
        const response = await fetch('/api/admin/tickets');

        console.log('Tickets response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Tickets API error:', response.status, errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const tickets = await response.json();
        console.log('Tickets received:', tickets);

        // Check if response has error
        if (tickets.error) {
            console.error('Tickets error:', tickets.error);
            showNotification(`Tickets error: ${tickets.error}`, 'error');

            const tbody = document.getElementById('tickets-tbody');
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">
                Error loading tickets: ${tickets.error}
            </td></tr>`;
            return;
        }

        const tbody = document.getElementById('tickets-tbody');
        if (!Array.isArray(tickets) || tickets.length === 0) {
            console.log('No tickets found');
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No tickets found</td></tr>';
            return;
        }

        console.log(`Rendering ${tickets.length} tickets`);
        tbody.innerHTML = tickets.map(ticket => `
            <tr class="fade-in">
                <td>#${ticket.id}</td>
                <td>${ticket.subject || 'No subject'}</td>
                <td>${ticket.category || 'Unknown'}</td>
                <td>${ticket.user_name || 'Anonymous'}</td>
                <td><span class="status-badge status-${ticket.status}">${ticket.status.replace('_', ' ')}</span></td>
                <td>${formatTime(ticket.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="viewTicket(${ticket.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="startChat(${ticket.id})">
                        <i class="fas fa-comments"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        console.log('Tickets rendered successfully');

    } catch (error) {
        console.error('Error loading tickets:', error);
        showNotification('Failed to load tickets. Please check the server connection.', 'error');

        const tbody = document.getElementById('tickets-tbody');
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">
            Failed to load tickets: ${error.message}
        </td></tr>`;
    }
}

function filterTickets() {
    const statusFilter = document.getElementById('status-filter').value;
    const categoryFilter = document.getElementById('category-filter').value;

    // Apply filters (implement filtering logic)
    loadTickets(); // For now, just reload all tickets
}

async function viewTicket(ticketId) {
    try {
        const response = await fetch(`/api/admin/tickets/${ticketId}`);
        const ticket = await response.json();

        document.getElementById('ticket-details').innerHTML = `
            <div class="ticket-info">
                <h6>Ticket #${ticket.id}</h6>
                <p><strong>Subject:</strong> ${ticket.subject}</p>
                <p><strong>Category:</strong> ${ticket.category}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${ticket.status}">${ticket.status.replace('_', ' ')}</span></p>
                <p><strong>User:</strong> ${ticket.user_name || 'Anonymous'}</p>
                <p><strong>Email:</strong> ${ticket.user_email || 'Not provided'}</p>
                <p><strong>Created:</strong> ${formatTime(ticket.created_at)}</p>
                <div class="ticket-messages">
                    <h6>Messages:</h6>
                    ${ticket.messages.map(msg => `
                        <div class="message-item ${msg.is_admin ? 'admin' : 'user'}">
                            <div class="message-header">
                                <strong>${msg.is_admin ? 'Admin' : (ticket.user_name || 'User')}</strong>
                                <span class="text-muted">${formatTime(msg.created_at)}</span>
                            </div>
                            <div class="message-body">${msg.content}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('ticketModal'));
        modal.show();

        currentTicketId = ticketId;
    } catch (error) {
        console.error('Error viewing ticket:', error);
    }
}

// Live Chat functions
async function loadActiveConversations() {
    try {
        const response = await fetch('/api/admin/active-conversations');
        const conversations = await response.json();

        const conversationsList = document.getElementById('conversations-list');
        if (conversations.length === 0) {
            conversationsList.innerHTML = '<p class="text-muted text-center">No active conversations</p>';
            return;
        }

        conversationsList.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${conv.id === currentTicketId ? 'active' : ''}" 
                 onclick="selectConversation(${conv.id})">
                <h6>${conv.user_name || 'Anonymous User'}</h6>
                <p>${conv.subject}</p>
                <small class="text-muted">${formatTime(conv.last_message_at)}</small>
                ${conv.unread_count > 0 ? `<span class="badge bg-primary">${conv.unread_count}</span>` : ''}
            </div>
        `).join('');

        // Update active conversations map
        conversations.forEach(conv => {
            activeConversations.set(conv.id, conv);
        });
    } catch (error) {
        console.error('Error loading active conversations:', error);
    }
}

async function selectConversation(ticketId) {
    currentTicketId = ticketId;

    // Update UI
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.conversation-item').classList.add('active');

    // Load conversation details
    const conversation = activeConversations.get(ticketId);
    if (conversation) {
        document.getElementById('chat-user-name').textContent =
            `${conversation.user_name || 'Anonymous'} - ${conversation.subject}`;
        document.getElementById('admin-chat-input').style.display = 'block';
    }

    // Load messages
    await loadChatMessages(ticketId);
}

async function loadChatMessages(ticketId) {
    try {
        const response = await fetch(`/api/tickets/${ticketId}/messages`);
        const messages = await response.json();

        const messagesContainer = document.getElementById('admin-chat-messages');
        messagesContainer.innerHTML = messages.map(msg => `
            <div class="chat-message ${msg.is_admin ? 'admin' : 'user'} fade-in">
                <div class="message-avatar ${msg.is_admin ? 'admin' : 'user'}">
                    ${msg.is_admin ? 'A' : 'U'}
                </div>
                <div class="message-content">
                    ${msg.content}
                    <div class="message-time">${formatTime(msg.created_at)}</div>
                </div>
            </div>
        `).join('');

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Error loading chat messages:', error);
    }
}

async function sendAdminMessage() {
    const input = document.getElementById('admin-message-input');
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
                is_admin: true
            })
        });

        if (response.ok) {
            input.value = '';
            await loadChatMessages(currentTicketId);
            await loadActiveConversations(); // Refresh conversations list
        }
    } catch (error) {
        console.error('Error sending admin message:', error);
    }
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        sendAdminMessage();
    }
}

async function updateTicketStatus(status) {
    if (!currentTicketId) return;

    let adminMessage = '';

    // If resolving or closing, ask for optional message
    if (status === 'resolved' || status === 'closed') {
        adminMessage = prompt(
            `${status === 'resolved' ? 'Resolving' : 'Closing'} ticket #${currentTicketId}.\n\n` +
            'Enter an optional message to send to the user (or leave blank for default message):'
        );

        // User cancelled the prompt
        if (adminMessage === null) return;
    }

    try {
        const requestBody = { status };
        if (adminMessage && adminMessage.trim()) {
            requestBody.message = adminMessage.trim();
        }

        const response = await fetch(`/api/admin/tickets/${currentTicketId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (response.ok) {
            const result = await response.json();

            // Refresh data
            await loadTickets();
            await loadActiveConversations();
            await loadDashboardData();

            // Show success message
            const notificationMessage = result.notification_sent
                ? `Ticket status updated to ${status} and user has been notified`
                : `Ticket status updated to ${status}`;

            showNotification(notificationMessage, 'success');

            // If ticket was closed, show additional info
            if (status === 'resolved' || status === 'closed') {
                console.log(`Ticket ${currentTicketId} ${status}. User notification: ${result.notification_sent}`);
            }
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.error || 'Failed to update ticket'}`, 'error');
        }
    } catch (error) {
        console.error('Error updating ticket status:', error);
        showNotification('Error updating ticket status', 'error');
    }
}

// Analytics functions
async function loadAnalytics() {
    try {
        const response = await fetch('/api/admin/analytics');
        const analytics = await response.json();

        // Create charts
        createCategoryChart(analytics.categoryData);
        createResolutionChart(analytics.resolutionData);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#667eea',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b',
                    '#f6d365'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createResolutionChart(data) {
    const ctx = document.getElementById('resolutionChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Resolution Time (hours)',
                data: data.values,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Utility functions
function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
    return date.toLocaleDateString();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function refreshData() {
    loadDashboardData();
    loadTickets();
    loadActiveConversations();
    showNotification('Data refreshed successfully', 'success');
}

function startAutoRefresh() {
    // Refresh live chat data every 10 seconds
    refreshInterval = setInterval(() => {
        if (document.getElementById('live-chat-section').classList.contains('active')) {
            loadActiveConversations();
            if (currentTicketId) {
                loadChatMessages(currentTicketId);
            }
        }
    }, 10000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

// Chat from ticket modal
function openLiveChat() {
    if (currentTicketId) {
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('ticketModal')).hide();

        // Switch to live chat section
        showSection('live-chat');

        // Select the conversation
        setTimeout(() => {
            selectConversation(currentTicketId);
        }, 100);
    }
}

function startChat(ticketId) {
    currentTicketId = ticketId;
    showSection('live-chat');
    setTimeout(() => {
        selectConversation(ticketId);
    }, 100);
}
