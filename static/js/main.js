/**
 * Main JavaScript for Healthcare Analytics Application
 * Handles UI interactions, form validations, and dynamic behaviors
 */

// ==================== DOM Ready ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize application
 */
function initializeApp() {
    console.log('Healthcare Analytics Application Initialized');
    setupNavigation();
    setupFormValidation();
    setupDropdownMenus();
}

// ==================== Navigation Functions ====================

/**
 * Setup navigation dropdown menus
 */
function setupDropdownMenus() {
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            const menu = this.querySelector('.dropdown-menu');
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        dropdowns.forEach(dropdown => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) menu.style.display = 'none';
        });
    });
}

/**
 * Setup navigation bar
 */
function setupNavigation() {
    const navLogo = document.querySelector('.nav-logo');
    if (navLogo) {
        navLogo.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
}

// ==================== Form Validation ====================

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showAlert('Please fill all required fields correctly', 'error');
            }
        });
    });
}

/**
 * Validate form fields
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            field.addEventListener('input', function() {
                this.classList.remove('error');
            });
        }
    });
    
    return isValid;
}

// ==================== Alert Functions ====================

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (info, error, success, warning)
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Get alert icon based on type
 * @param {string} type - Alert type
 * @returns {string} - Icon name
 */
function getAlertIcon(type) {
    const icons = {
        'error': 'exclamation-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || icons['info'];
}

// ==================== Utility Functions ====================

/**
 * Format number to 2 decimal places
 * @param {number} value - Value to format
 * @returns {string} - Formatted value
 */
function formatNumber(value) {
    return parseFloat(value).toFixed(2);
}

/**
 * Format date to readable string
 * @param {string} dateString - Date string
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Show loading indicator
 * @param {string} message - Loading message
 */
function showLoading(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = `
        <div class="spinner"></div>
        <p>${message}</p>
    `;
    document.body.appendChild(loader);
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    const loader = document.querySelector('.loader');
    if (loader) loader.remove();
}

// ==================== Data Table Functions ====================

/**
 * Filter table by search term
 * @param {string} tableId - Table element ID
 * @param {number} columnIndex - Column index to search
 */
function filterTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const input = document.querySelector('[data-filter-table="' + tableId + '"]');
    if (!input) return;
    
    const filterValue = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    
    Array.from(rows).forEach(row => {
        const cell = row.getElementsByTagName('td')[columnIndex];
        if (cell && cell.textContent.toLowerCase().includes(filterValue)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// ==================== Export Functions ====================

/**
 * Export table to CSV
 * @param {string} tableId - Table element ID
 * @param {string} filename - Output filename
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.getElementsByTagName('tr');
    
    Array.from(rows).forEach(row => {
        const cells = row.getElementsByTagName('th,td');
        const rowData = Array.from(cells).map(cell => {
            let text = cell.textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            text = text.replace(/"/g, '""');
            return text.includes(',') ? `"${text}"` : text;
        });
        csv.push(rowData.join(','));
    });
    
    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// ==================== API Functions ====================

/**
 * Fetch data from API
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} - API response
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('An error occurred. Please try again.', 'error');
        throw error;
    }
}

// ==================== Input Validation Functions ====================

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} - True if valid
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} - Validation result with strength level
 */
function validatePassword(password) {
    let strength = 'weak';
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.match(/[a-z]/)) score++;
    if (password.match(/[A-Z]/)) score++;
    if (password.match(/[0-9]/)) score++;
    if (password.match(/[^a-zA-Z0-9]/)) score++;
    
    if (score >= 4) strength = 'strong';
    else if (score >= 2) strength = 'medium';
    
    return {
        valid: password.length >= 6,
        strength: strength,
        score: score
    };
}

/**
 * Validate number range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} - True if in range
 */
function validateRange(value, min, max) {
    const num = parseFloat(value);
    return num >= min && num <= max;
}

// ==================== Charts and Visualization ====================

/**
 * Create a simple chart (placeholder for actual chart library)
 * @param {string} elementId - Element ID for chart
 * @param {array} data - Chart data
 * @param {string} type - Chart type
 */
function createChart(elementId, data, type = 'bar') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    console.log(`Creating ${type} chart with data:`, data);
    // This would use a charting library like Chart.js in production
}

// ==================== Progress Bar Functions ====================

/**
 * Update progress bar
 * @param {string} elementId - Progress bar element ID
 * @param {number} value - Progress value (0-100)
 */
function updateProgress(elementId, value) {
    const progressBar = document.getElementById(elementId);
    if (!progressBar) return;
    
    const fillElement = progressBar.querySelector('.progress-fill');
    if (fillElement) {
        fillElement.style.width = value + '%';
    }
}

// ==================== Modal Functions ====================

/**
 * Show modal
 * @param {string} modalId - Modal element ID
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('fade-in');
    }
}

/**
 * Close modal
 * @param {string} modalId - Modal element ID
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ==================== Local Storage Functions ====================

/**
 * Save data to local storage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Storage Error:', error);
    }
}

/**
 * Get data from local storage
 * @param {string} key - Storage key
 * @returns {any} - Stored value or null
 */
function getFromStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Storage Error:', error);
        return null;
    }
}

/**
 * Remove data from local storage
 * @param {string} key - Storage key
 */
function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Storage Error:', error);
    }
}

// ==================== Keyboard Shortcuts ====================

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + S: Save
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            // Handle save action
        }
        
        // Escape: Close modal
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('[role="modal"]');
            modals.forEach(modal => modal.style.display = 'none');
        }
    });
}

// ==================== Export Functions ====================
window.showAlert = showAlert;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.filterTable = filterTable;
window.exportTableToCSV = exportTableToCSV;
window.validateEmail = validateEmail;
window.validatePassword = validatePassword;
window.validateRange = validateRange;
window.updateProgress = updateProgress;
window.showModal = showModal;
window.closeModal = closeModal;
window.saveToStorage = saveToStorage;
window.getFromStorage = getFromStorage;
window.removeFromStorage = removeFromStorage;
