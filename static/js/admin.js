// Admin Dashboard JavaScript
let currentTicketId = null;
let activeConversations = new Map();
let refreshInterval = null;

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Starting admin dashboard initialization...');

    // Test if we can reach the server
    fetch('/api/admin/dashboard-stats')
        .then(response => {
            console.log('Initial server test response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Initial server test data:', data);
        })
        .catch(error => {
            console.error('Initial server test failed:', error);
        });

    loadDashboardData();
    loadCategories();
    loadTickets();
    loadActiveConversations();

    // Start auto-refresh for live chat
    startAutoRefresh();

    console.log('Admin dashboard initialization complete');
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
    console.log('=== loadDashboardData CALLED ===');
    console.log('Current URL:', window.location.href);
    console.log('Fetching dashboard stats...');

    try {
        console.log('Loading dashboard data...');

        // Add timeout to the fetch request
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const response = await fetch('/api/admin/dashboard-stats', {
            signal: controller.signal
        });

        clearTimeout(timeoutId);
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

        // Update dashboard stats with fallback values
        const totalElement = document.getElementById('total-tickets');
        const pendingElement = document.getElementById('pending-tickets');
        const resolvedElement = document.getElementById('resolved-tickets');
        const activeElement = document.getElementById('active-chats');

        if (totalElement) totalElement.textContent = stats.totalTickets || 0;
        if (pendingElement) pendingElement.textContent = stats.pendingTickets || 0;
        if (resolvedElement) resolvedElement.textContent = stats.resolvedTickets || 0;
        if (activeElement) activeElement.textContent = stats.activeChats || 0;

        console.log('Dashboard stats updated successfully');

        // Load recent activity after dashboard stats are loaded
        loadRecentActivity();

    } catch (error) {
        console.error('Error loading dashboard data:', error);

        let errorMessage = 'Failed to load dashboard data. ';
        if (error.name === 'AbortError') {
            errorMessage += 'Request timed out.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Please check if the server is running.';
        } else {
            errorMessage += 'Please check the server connection.';
        }

        showNotification(errorMessage, 'error');

        // Set fallback values with proper null checks
        const elements = [
            'total-tickets', 'pending-tickets', 'resolved-tickets', 'active-chats'
        ];

        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '?';
            }
        });
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
                <td><span class="priority-badge priority-${ticket.priority || 'medium'}">${(ticket.priority || 'medium').toUpperCase()}</span></td>
                <td class="organization-cell">
                    <div class="organization-name">${ticket.organization || 'Unknown Org'}</div>
                    <small class="text-muted">${ticket.user_name || 'Anonymous'}</small>
                </td>
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
    const priorityFilter = document.getElementById('priority-filter').value;
    const categoryFilter = document.getElementById('category-filter').value;
    const organizationFilter = document.getElementById('organization-filter').value.toLowerCase();

    const rows = document.querySelectorAll('#tickets-tbody tr');

    rows.forEach(row => {
        const cells = row.cells;
        if (cells.length < 8) return; // Skip header or malformed rows

        const status = cells[6].textContent.toLowerCase().trim();
        const priority = cells[2].textContent.toLowerCase().trim();
        const category = cells[4].textContent.toLowerCase().trim();
        const organization = cells[3].textContent.toLowerCase().trim();

        const statusMatch = !statusFilter || status.includes(statusFilter.replace('_', ' '));
        const priorityMatch = !priorityFilter || priority.includes(priorityFilter);
        const categoryMatch = !categoryFilter || category.includes(categoryFilter.toLowerCase());
        const organizationMatch = !organizationFilter || organization.includes(organizationFilter);

        if (statusMatch && priorityMatch && categoryMatch && organizationMatch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

async function viewTicket(ticketId) {
    try {
        console.log(`Loading ticket details for ticket ID: ${ticketId}`);
        const response = await fetch(`/api/admin/tickets/${ticketId}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const ticket = await response.json();
        console.log('Ticket data loaded:', ticket);

        // Check if we have messages with attachments
        if (ticket.messages) {
            ticket.messages.forEach((msg, index) => {
                console.log(`Message ${index + 1}:`, {
                    content: msg.content.substring(0, 50) + '...',
                    has_attachments: msg.attachments && msg.attachments.length > 0,
                    attachment_count: msg.attachments ? msg.attachments.length : 0,
                    attachment_url: msg.attachment_url,
                    attachments: msg.attachments
                });
            });
        }

        document.getElementById('ticket-details').innerHTML = `
            <div class="ticket-info">
                <h6>Ticket #${ticket.id}</h6>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Subject:</strong> ${ticket.subject}</p>
                        <p><strong>Category:</strong> ${ticket.category}</p>
                        <p><strong>Priority:</strong> <span class="priority-badge priority-${ticket.priority || 'medium'}">${(ticket.priority || 'medium').toUpperCase()}</span></p>
                        <p><strong>Status:</strong> <span class="status-badge status-${ticket.status}">${ticket.status.replace('_', ' ')}</span></p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Organization:</strong> <span class="fw-bold text-primary">${ticket.organization || 'Unknown Organization'}</span></p>
                        <p><strong>User:</strong> ${ticket.user_name || 'Anonymous'}</p>
                        <p><strong>Email:</strong> ${ticket.user_email || 'Not provided'}</p>
                        <p><strong>Created:</strong> ${formatTime(ticket.created_at)}</p>
                    </div>
                </div>
                <div class="ticket-messages">
                    <h6>Messages:</h6>
                    ${ticket.messages.map(msg => {
            console.log('Processing message for rendering:', {
                hasAttachments: msg.attachments && msg.attachments.length > 0,
                attachmentUrl: msg.attachment_url,
                attachmentCount: msg.attachments ? msg.attachments.length : 0
            });

            return `
                        <div class="message-item ${msg.is_admin ? 'admin' : 'user'}">
                            <div class="message-header">
                                <strong>${msg.is_admin ? 'Admin' : (ticket.user_name || 'User')}</strong>
                                <span class="text-muted">${formatTime(msg.created_at)}</span>
                            </div>
                            <div class="message-body">${msg.content}</div>
                            ${(msg.attachments && msg.attachments.length > 0) || (msg.attachment_url) ? `
                                <div class="message-attachments">
                                    <h6 class="mt-2 mb-1"><i class="fas fa-paperclip"></i> Attachments:</h6>
                                    <div class="attachments-grid">
                                        ${msg.attachments && msg.attachments.length > 0 ? msg.attachments.map(att => {
                console.log('Processing attachment:', att);
                const attachmentUrl = att.url || att.file_path || `/static/uploads/${att.filename || att.stored_name}`;
                console.log('Final attachment URL:', attachmentUrl);

                return `
                                            <div class="attachment-item" style="margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; display: inline-block;">
                                                <div class="attachment-preview" style="text-align: center;">
                                                    <img src="${attachmentUrl}" alt="${att.original_name || att.filename}" 
                                                         class="attachment-thumbnail" 
                                                         onclick="openImageModal('${attachmentUrl}', '${att.original_name || att.filename}')" 
                                                         style="cursor: pointer; max-width: 150px; max-height: 150px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                                                         onerror="console.error('Failed to load image:', this.src); this.style.display='none'; this.nextElementSibling.style.display='block';">
                                                    <div class="file-icon" style="display: none; font-size: 48px; color: #666;">
                                                        <i class="fas fa-file-image"></i>
                                                        <div style="font-size: 12px; margin-top: 5px;">Image not found</div>
                                                    </div>
                                                </div>
                                                <div class="attachment-info" style="text-align: center; margin-top: 5px;">
                                                    <div><small><strong>${att.original_name || att.filename}</strong></small></div>
                                                    <div><small class="text-muted">(${formatFileSize(att.file_size || 0)})</small></div>
                                                    <div>
                                                        <a href="${attachmentUrl}" target="_blank" class="btn btn-sm btn-outline-primary mt-1">
                                                            <i class="fas fa-external-link-alt"></i> View
                                                        </a>
                                                        <button onclick="testImageUrl('${attachmentUrl}')" class="btn btn-sm btn-outline-info mt-1">
                                                            <i class="fas fa-search"></i> Test
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                            `;
            }).join('') : ''}
                                        ${msg.attachment_url ? `
                                            <div class="attachment-item" style="margin: 5px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; display: inline-block;">
                                                <div class="attachment-preview" style="text-align: center;">
                                                    <img src="${msg.attachment_url}" alt="Attachment" 
                                                         class="attachment-thumbnail" 
                                                         onclick="openImageModal('${msg.attachment_url}', 'attachment')" 
                                                         style="cursor: pointer; max-width: 150px; max-height: 150px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                                                         onerror="console.error('Failed to load image:', this.src); this.style.display='none'; this.nextElementSibling.style.display='block';">
                                                    <div class="file-icon" style="display: none; font-size: 48px; color: #666;">
                                                        <i class="fas fa-file-image"></i>
                                                        <div style="font-size: 12px; margin-top: 5px;">Image not found</div>
                                                    </div>
                                                </div>
                                                <div class="attachment-info" style="text-align: center; margin-top: 5px;">
                                                    <div><small><strong>Attachment</strong></small></div>
                                                    <div>
                                                        <a href="${msg.attachment_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-1">
                                                            <i class="fas fa-external-link-alt"></i> View
                                                        </a>
                                                        <button onclick="testImageUrl('${msg.attachment_url}')" class="btn btn-sm btn-outline-info mt-1">
                                                            <i class="fas fa-search"></i> Test
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('ticketModal'));
        modal.show();

        currentTicketId = ticketId;
    } catch (error) {
        console.error('Error viewing ticket:', error);
        showNotification('Error loading ticket details: ' + error.message, 'error');
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
        const messages = await response.json(); const messagesContainer = document.getElementById('admin-chat-messages');
        messagesContainer.innerHTML = messages.map(msg => `
            <div class="chat-message ${msg.is_admin ? 'admin' : 'user'} fade-in">
                <div class="message-avatar ${msg.is_admin ? 'admin' : 'user'}">
                    ${msg.is_admin ? 'A' : 'U'}
                </div>
                <div class="message-content">
                    ${msg.content}
                    ${msg.attachments && msg.attachments.length > 0 ? `
                        <div class="message-attachments">
                            ${msg.attachments.map(att => `
                                <div class="attachment-item">
                                    <img src="${att.url}" alt="${att.original_name}" class="attachment-thumbnail" onclick="openImageModal('${att.url}', '${att.original_name}')">
                                    <div class="attachment-info">
                                        <small>${att.original_name}</small>
                                        <small class="text-muted">(${formatFileSize(att.file_size)})</small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
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

// Admin authentication functions
function adminLogout() {
    if (confirm('Are you sure you want to logout from the admin panel?')) {
        window.location.href = '/auth/admin/logout';
    }
}

// Check admin authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    // Add authentication check for admin APIs
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        return originalFetch.apply(this, args)
            .then(response => {
                if (response.status === 401) {
                    // Admin session expired
                    alert('Admin session expired. Please login again.');
                    window.location.href = '/auth/admin/login';
                    return Promise.reject(new Error('Authentication required'));
                }
                return response;
            })
            .catch(error => {
                console.error('Fetch error:', error);
                throw error;
            });
    };
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

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Function to open image in modal
function openImageModal(imageUrl, imageName) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('imageModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'imageModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="imageModalTitle">Image Attachment</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="modalImage" class="img-fluid" style="max-height: 70vh;">
                    </div>
                    <div class="modal-footer">
                        <a id="downloadImageBtn" class="btn btn-primary" download>
                            <i class="fas fa-download"></i> Download
                        </a>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Update modal content
    document.getElementById('imageModalTitle').textContent = imageName;
    document.getElementById('modalImage').src = imageUrl;
    document.getElementById('downloadImageBtn').href = imageUrl;
    document.getElementById('downloadImageBtn').download = imageName;

    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Helper function to test image URLs for debugging
function testImageUrl(url) {
    console.log('Testing image URL:', url);

    // Test if the URL is reachable
    fetch(url, { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                console.log('✅ Image URL is accessible:', url);
                showNotification(`Image URL is accessible: ${url}`, 'success');
            } else {
                console.error('❌ Image URL not accessible:', url, 'Status:', response.status);
                showNotification(`Image URL not accessible (${response.status}): ${url}`, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error testing image URL:', url, error);
            showNotification(`Error accessing image URL: ${url}`, 'error');
        });

    // Also try to open in new tab for manual verification
    window.open(url, '_blank');
}
