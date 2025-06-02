// Global variables
let currentTicketId = null;
let selectedCategory = null;
let currentUser = null;

// Initialize chat when document is ready
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
});

// Load categories from backend
async function loadCategories() {
    try {
        console.log('Fetching categories...'); // Debug log
        const response = await fetch('/api/categories');
        console.log('Response status:', response.status); // Debug log

        const categories = await response.json();
        console.log('Categories received:', categories); // Debug log

        const categoriesDiv = document.getElementById('categories');
        if (!categoriesDiv) {
            console.error('Categories div not found!');
            return;
        }

        if (Array.isArray(categories)) {
            categoriesDiv.innerHTML = categories.map(category => `
                <button class="category-btn" onclick="selectCategory(${category.id}, '${category.name}')">
                    ${category.name}
                </button>
            `).join('');
        } else {
            console.error('Invalid categories data:', categories);
            addMessage('Error loading categories. Please try again.', 'system');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        addMessage('System error. Please try again later.', 'system');
    }
}

// Handle category selection
async function selectCategory(categoryId, categoryName) {
    selectedCategory = { id: categoryId, name: categoryName };

    try {
        // Load common queries for this category
        const response = await fetch(`/api/common-queries/${categoryId}`);
        const queries = await response.json();

        // Clear previous messages
        const messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML = '';

        // Add category selection message
        addMessage(`You selected: ${categoryName}`, 'system');

        if (queries.length > 0) {
            addMessage('Here are some common solutions. Click one that matches your issue:', 'system');

            // Display common queries
            const queriesHtml = queries.map(query => `
                <div class="query-item" onclick="showSolution('${query.question}', '${query.solution.replace(/'/g, "\\'")}')">
                    ${query.question}
                </div>
            `).join('');

            addHTML(`<div class="common-queries">${queriesHtml}</div>`);
        } else {
            showTicketForm();
        }
    } catch (error) {
        console.error('Error loading common queries:', error);
        addMessage('System error. Please try again later.', 'system');
    }
}

// Show solution in modal
function showSolution(question, solution) {
    const modal = new bootstrap.Modal(document.getElementById('solutionModal'));
    document.getElementById('solution-content').innerHTML = `
        <h6>${question}</h6>
        <p>${solution}</p>
    `;
    modal.show();
}

// Show ticket creation form
function showTicketForm() {
    const formHtml = `
        <div class="user-info-form">
            <input type="text" class="form-control" id="user-name" placeholder="Your Name (optional)">
            <input type="email" class="form-control" id="user-email" placeholder="Your Email (optional)">
            <textarea class="form-control" id="ticket-message" placeholder="Please describe your issue" rows="3"></textarea>
            <button class="btn btn-primary mt-2" onclick="submitTicket()">Submit</button>
        </div>
    `;

    addHTML(formHtml);
}

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
