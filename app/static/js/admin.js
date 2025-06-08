// Admin Panel JavaScript - YouCloudPay Devshop Support System

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeAdminPanel();
});

function initializeAdminPanel() {
    initializeCharts();
    initializeDataTables();
    initializeModalHandlers();
    initializeFormSubmissions();
    initializeNotifications();
    initializeFilters();
    startAutoRefresh();
}

// Chart Initialization
function initializeCharts() {
    // Dashboard Analytics Charts
    if (document.getElementById('complaintsChart')) {
        initializeComplaintsChart();
    }

    if (document.getElementById('responseTimeChart')) {
        initializeResponseTimeChart();
    }

    if (document.getElementById('satisfactionChart')) {
        initializeSatisfactionChart();
    }

    if (document.getElementById('volumeChart')) {
        initializeVolumeChart();
    }
}

function initializeComplaintsChart() {
    const ctx = document.getElementById('complaintsChart').getContext('2d');

    // Fetch data from API
    fetch('/api/admin/analytics/complaints-trend')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Open Complaints',
                        data: data.open,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Resolved Complaints',
                        data: data.resolved,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Complaints Trend (Last 30 Days)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading complaints chart:', error));
}

function initializeResponseTimeChart() {
    const ctx = document.getElementById('responseTimeChart').getContext('2d');

    fetch('/api/admin/analytics/response-times')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Average Response Time (hours)',
                        data: data.values,
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#f59e0b',
                            '#ef4444',
                            '#8b5cf6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Average Response Time by Priority'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Hours'
                            }
                        }
                    }
                }
            });
        });
}

function initializeSatisfactionChart() {
    const ctx = document.getElementById('satisfactionChart').getContext('2d');

    fetch('/api/admin/analytics/satisfaction')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied'],
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            '#10b981',
                            '#34d399',
                            '#fbbf24',
                            '#fb923c',
                            '#ef4444'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Customer Satisfaction Ratings'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        });
}

function initializeVolumeChart() {
    const ctx = document.getElementById('volumeChart').getContext('2d');

    fetch('/api/admin/analytics/volume-by-hour')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Support Requests',
                        data: data.values,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Support Volume by Hour (Last 7 Days)'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Hour of Day'
                            }
                        }
                    }
                }
            });
        });
}

// Data Tables Initialization
function initializeDataTables() {
    // Users Table
    if (document.getElementById('usersTable')) {
        $('#usersTable').DataTable({
            processing: true,
            serverSide: true,
            ajax: '/api/admin/users',
            columns: [
                { data: 'id' },
                { data: 'username' },
                { data: 'email' },
                { data: 'role' },
                { data: 'created_at' },
                { data: 'last_login' },
                { data: 'status' },
                { data: 'actions', orderable: false, searchable: false }
            ],
            order: [[0, 'desc']],
            pageLength: 25,
            responsive: true
        });
    }

    // Complaints Table
    if (document.getElementById('complaintsTable')) {
        $('#complaintsTable').DataTable({
            processing: true,
            serverSide: true,
            ajax: '/api/admin/complaints',
            columns: [
                { data: 'id' },
                { data: 'title' },
                { data: 'user' },
                { data: 'priority' },
                { data: 'status' },
                { data: 'created_at' },
                { data: 'updated_at' },
                { data: 'actions', orderable: false, searchable: false }
            ],
            order: [[0, 'desc']],
            pageLength: 25,
            responsive: true
        });
    }
}

// Modal Handlers
function initializeModalHandlers() {
    // User management modals
    document.querySelectorAll('.edit-user-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const userId = this.dataset.userId;
            loadUserData(userId);
        });
    });

    // Complaint management modals
    document.querySelectorAll('.view-complaint-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const complaintId = this.dataset.complaintId;
            loadComplaintData(complaintId);
        });
    });

    // Close modal handlers
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function () {
            closeModal(this.closest('.modal'));
        });
    });
}

function loadUserData(userId) {
    fetch(`/api/admin/users/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateUserModal(data.user);
                showModal('userModal');
            } else {
                showNotification('Error loading user data', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error loading user data', 'error');
        });
}

function loadComplaintData(complaintId) {
    fetch(`/api/admin/complaints/${complaintId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateComplaintModal(data.complaint);
                showModal('complaintModal');
            } else {
                showNotification('Error loading complaint data', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error loading complaint data', 'error');
        });
}

function populateUserModal(user) {
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUsername').value = user.username;
    document.getElementById('editEmail').value = user.email;
    document.getElementById('editRole').value = user.role;
    document.getElementById('editStatus').value = user.is_active ? 'active' : 'inactive';
}

function populateComplaintModal(complaint) {
    document.getElementById('complaintTitle').textContent = complaint.title;
    document.getElementById('complaintDescription').textContent = complaint.description;
    document.getElementById('complaintUser').textContent = complaint.user.username;
    document.getElementById('complaintPriority').textContent = complaint.priority;
    document.getElementById('complaintStatus').textContent = complaint.status;
    document.getElementById('complaintCreated').textContent = formatDate(complaint.created_at);

    // Load complaint messages
    loadComplaintMessages(complaint.id);
}

function loadComplaintMessages(complaintId) {
    fetch(`/api/admin/complaints/${complaintId}/messages`)
        .then(response => response.json())
        .then(data => {
            const messagesContainer = document.getElementById('complaintMessages');
            messagesContainer.innerHTML = '';

            data.messages.forEach(message => {
                const messageElement = createMessageElement(message);
                messagesContainer.appendChild(messageElement);
            });
        });
}

function createMessageElement(message) {
    const div = document.createElement('div');
    div.className = `message ${message.is_from_user ? 'user-message' : 'admin-message'}`;

    div.innerHTML = `
        <div class="message-header">
            <span class="sender">${message.sender}</span>
            <span class="timestamp">${formatDate(message.created_at)}</span>
        </div>
        <div class="message-content">${message.content}</div>
    `;

    return div;
}

// Form Submissions
function initializeFormSubmissions() {
    // User edit form
    const userEditForm = document.getElementById('userEditForm');
    if (userEditForm) {
        userEditForm.addEventListener('submit', function (e) {
            e.preventDefault();
            submitUserEdit();
        });
    }

    // Complaint status update form
    const complaintStatusForm = document.getElementById('complaintStatusForm');
    if (complaintStatusForm) {
        complaintStatusForm.addEventListener('submit', function (e) {
            e.preventDefault();
            updateComplaintStatus();
        });
    }

    // Admin reply form
    const adminReplyForm = document.getElementById('adminReplyForm');
    if (adminReplyForm) {
        adminReplyForm.addEventListener('submit', function (e) {
            e.preventDefault();
            submitAdminReply();
        });
    }
}

function submitUserEdit() {
    const formData = new FormData(document.getElementById('userEditForm'));
    const userId = formData.get('userId');

    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        role: formData.get('role'),
        is_active: formData.get('status') === 'active'
    };

    fetch(`/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(userData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('User updated successfully', 'success');
                closeModal('userModal');
                refreshUsersTable();
            } else {
                showNotification(data.message || 'Error updating user', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating user', 'error');
        });
}

function updateComplaintStatus() {
    const formData = new FormData(document.getElementById('complaintStatusForm'));
    const complaintId = formData.get('complaintId');
    const status = formData.get('status');

    fetch(`/api/admin/complaints/${complaintId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ status: status })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Complaint status updated', 'success');
                refreshComplaintsTable();
            } else {
                showNotification(data.message || 'Error updating status', 'error');
            }
        });
}

function submitAdminReply() {
    const formData = new FormData(document.getElementById('adminReplyForm'));
    const complaintId = formData.get('complaintId');
    const message = formData.get('message');

    fetch(`/api/admin/complaints/${complaintId}/reply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ message: message })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Reply sent successfully', 'success');
                document.getElementById('adminReplyForm').reset();
                loadComplaintMessages(complaintId);
            } else {
                showNotification(data.message || 'Error sending reply', 'error');
            }
        });
}

// Notifications
function initializeNotifications() {
    // Check for new notifications periodically
    setInterval(checkForNotifications, 30000); // Every 30 seconds
}

function checkForNotifications() {
    fetch('/api/admin/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.notifications && data.notifications.length > 0) {
                updateNotificationBadge(data.notifications.length);
                displayNotifications(data.notifications);
            }
        });
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

function displayNotifications(notifications) {
    const container = document.getElementById('notificationsContainer');
    if (container) {
        container.innerHTML = '';

        notifications.forEach(notification => {
            const element = createNotificationElement(notification);
            container.appendChild(element);
        });
    }
}

function createNotificationElement(notification) {
    const div = document.createElement('div');
    div.className = `notification-item ${notification.priority}`;

    div.innerHTML = `
        <div class="notification-content">
            <div class="notification-title">${notification.title}</div>
            <div class="notification-message">${notification.message}</div>
            <div class="notification-time">${formatDate(notification.created_at)}</div>
        </div>
        <button class="notification-dismiss" onclick="dismissNotification(${notification.id})">
            <i class="fas fa-times"></i>
        </button>
    `;

    return div;
}

function dismissNotification(notificationId) {
    fetch(`/api/admin/notifications/${notificationId}/dismiss`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                checkForNotifications(); // Refresh notifications
            }
        });
}

// Filters
function initializeFilters() {
    // Date range picker
    if (document.getElementById('dateRangePicker')) {
        flatpickr('#dateRangePicker', {
            mode: 'range',
            dateFormat: 'Y-m-d',
            onChange: function (selectedDates) {
                if (selectedDates.length === 2) {
                    applyDateFilter(selectedDates[0], selectedDates[1]);
                }
            }
        });
    }

    // Status filters
    document.querySelectorAll('.status-filter').forEach(filter => {
        filter.addEventListener('change', function () {
            applyStatusFilter();
        });
    });

    // Priority filters
    document.querySelectorAll('.priority-filter').forEach(filter => {
        filter.addEventListener('change', function () {
            applyPriorityFilter();
        });
    });
}

function applyDateFilter(startDate, endDate) {
    const table = $('#complaintsTable').DataTable();
    table.ajax.url(`/api/admin/complaints?start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`);
    table.ajax.reload();
}

function applyStatusFilter() {
    const selectedStatuses = Array.from(document.querySelectorAll('.status-filter:checked'))
        .map(checkbox => checkbox.value);

    const table = $('#complaintsTable').DataTable();
    table.ajax.url(`/api/admin/complaints?status=${selectedStatuses.join(',')}`);
    table.ajax.reload();
}

function applyPriorityFilter() {
    const selectedPriorities = Array.from(document.querySelectorAll('.priority-filter:checked'))
        .map(checkbox => checkbox.value);

    const table = $('#complaintsTable').DataTable();
    table.ajax.url(`/api/admin/complaints?priority=${selectedPriorities.join(',')}`);
    table.ajax.reload();
}

// Auto-refresh functionality
function startAutoRefresh() {
    // Refresh dashboard stats every 5 minutes
    setInterval(refreshDashboardStats, 300000);

    // Refresh charts every 10 minutes
    setInterval(refreshCharts, 600000);
}

function refreshDashboardStats() {
    fetch('/api/admin/dashboard-stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        });
}

function updateDashboardStats(stats) {
    if (document.getElementById('totalUsers')) {
        document.getElementById('totalUsers').textContent = stats.total_users;
    }
    if (document.getElementById('activeComplaints')) {
        document.getElementById('activeComplaints').textContent = stats.active_complaints;
    }
    if (document.getElementById('avgResponseTime')) {
        document.getElementById('avgResponseTime').textContent = stats.avg_response_time;
    }
    if (document.getElementById('satisfactionScore')) {
        document.getElementById('satisfactionScore').textContent = stats.satisfaction_score;
    }
}

function refreshCharts() {
    // Destroy existing charts and reinitialize
    Chart.helpers.each(Chart.instances, function (instance) {
        instance.destroy();
    });

    initializeCharts();
}

// Utility Functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.classList.add('modal-open');
    }
}

function closeModal(modalId) {
    const modal = typeof modalId === 'string' ? document.getElementById(modalId) : modalId;
    if (modal) {
        modal.classList.add('hidden');
        document.body.classList.remove('modal-open');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    const container = document.getElementById('notificationContainer') || document.body;
    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function refreshUsersTable() {
    const table = $('#usersTable').DataTable();
    if (table) {
        table.ajax.reload();
    }
}

function refreshComplaintsTable() {
    const table = $('#complaintsTable').DataTable();
    if (table) {
        table.ajax.reload();
    }
}

function formatDate(date) {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function getCSRFToken() {
    return document.querySelector('meta[name=csrf-token]').getAttribute('content');
}

// Export functions for global access
window.AdminPanel = {
    showModal,
    closeModal,
    showNotification,
    refreshUsersTable,
    refreshComplaintsTable,
    loadUserData,
    loadComplaintData,
    dismissNotification
};
