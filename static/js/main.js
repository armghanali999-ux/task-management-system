// Main JavaScript for Task Management System

document.addEventListener('DOMContentLoaded', function() {
    console.log('TaskFlow application loaded');
    initializeApp();
});

function initializeApp() {
    // Initialize theme
    initializeTheme();

    // Load dashboard data if on dashboard
    if (document.getElementById('project-count')) {
        loadDashboardData();
    }
}

function initializeTheme() {
    const theme = localStorage.getItem('app-theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

function toggleTheme() {
    const body = document.body;
    const theme = body.classList.contains('dark-theme') ? 'light' : 'dark';

    if (theme === 'dark') {
        body.classList.add('dark-theme');
    } else {
        body.classList.remove('dark-theme');
    }

    localStorage.setItem('app-theme', theme);
}

async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/', {
            headers: {
                'Authorization': `Token ${getAuthToken()}`
            }
        });

        if (!response.ok) {
            console.error('Failed to load dashboard data');
            return;
        }

        const data = await response.json();
        updateDashboardUI(data);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardUI(data) {
    const summary = data.summary || {};
    const tasksByStatus = data.tasks_by_status || {};

    document.getElementById('project-count').textContent = summary.total_projects || 0;
    document.getElementById('task-count').textContent = summary.total_tasks || 0;
    document.getElementById('progress-count').textContent = summary.in_progress_tasks || 0;
    document.getElementById('overdue-count').textContent = summary.overdue_tasks || 0;
}

function getAuthToken() {
    // Get token from localStorage or sessionStorage
    return localStorage.getItem('auth-token') || '';
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function handleError(error) {
    console.error('Error:', error);
    showNotification(`Error: ${error.message}`, 'danger');
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function getTaskStatusColor(status) {
    const colors = {
        'to_do': '#e7f1ff',
        'in_progress': '#fff3cd',
        'under_review': '#e2e3e5',
        'completed': '#d4edda',
        'cancelled': '#f8d7da'
    };
    return colors[status] || '#f0f0f0';
}

function getTaskPriorityLabel(priority) {
    const labels = {
        'low': '🟢 Low',
        'medium': '🟡 Medium',
        'high': '🟠 High',
        'critical': '🔴 Critical'
    };
    return labels[priority] || priority;
}
