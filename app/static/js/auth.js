// Authentication-specific JavaScript functionality

// Form Validation and Submission
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.auth-form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Basic validation
            if (!email || !password) {
                showNotification('Please fill in all required fields.', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address.', 'error');
                return;
            }
            
            // Simulate form submission (in real app, this would be handled by Flask)
            showNotification('Login functionality will be handled by the backend.', 'info');
            this.submit(); // Submit the form normally
        });
    }
});

// Registration Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('.auth-form');
    
    if (registerForm && registerForm.action.includes('register')) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const firstName = formData.get('first_name');
            const lastName = formData.get('last_name');
            const email = formData.get('email');
            const password = formData.get('password');
            const confirmPassword = formData.get('confirm_password');
            const experienceLevel = formData.get('experience_level');
            const interests = formData.get('interests');
            const terms = formData.get('terms');
            
            // Basic validation
            if (!firstName || !lastName || !email || !password || !confirmPassword || !experienceLevel || !interests || !terms) {
                showNotification('Please fill in all required fields.', 'error');
                return;
            }
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address.', 'error');
                return;
            }
            
            if (password !== confirmPassword) {
                showNotification('Passwords do not match.', 'error');
                return;
            }
            
            if (password.length < 8) {
                showNotification('Password must be at least 8 characters long.', 'error');
                return;
            }
            
            // Simulate form submission
            showNotification('Registration functionality will be handled by the backend.', 'info');
            this.submit(); // Submit the form normally
        });
    }
});

// Email validation helper function
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Password strength indicator
document.addEventListener('DOMContentLoaded', function() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    passwordInputs.forEach(input => {
        if (input.name === 'password') {
            input.addEventListener('input', function() {
                const password = this.value;
                const strength = calculatePasswordStrength(password);
                updatePasswordStrengthIndicator(this, strength);
            });
        }
    });
});

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (score < 2) return 'weak';
    if (score < 4) return 'medium';
    return 'strong';
}

function updatePasswordStrengthIndicator(input, strength) {
    let indicator = input.parentNode.querySelector('.password-strength');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength';
        indicator.style.cssText = `
            margin-top: 0.5rem;
            height: 4px;
            border-radius: 2px;
            transition: all 0.3s ease;
        `;
        input.parentNode.appendChild(indicator);
    }
    
    const colors = {
        weak: '#dc3545',
        medium: '#ffc107',
        strong: '#28a745'
    };
    
    const widths = {
        weak: '33%',
        medium: '66%',
        strong: '100%'
    };
    
    indicator.style.backgroundColor = colors[strength];
    indicator.style.width = widths[strength];
}

// Social Login Handlers
document.addEventListener('DOMContentLoaded', function() {
    const googleButtons = document.querySelectorAll('.btn-google');
    const microsoftButtons = document.querySelectorAll('.btn-microsoft');
    
    googleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            showNotification('Google authentication coming soon!', 'info');
        });
    });
    
    microsoftButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            showNotification('Microsoft authentication coming soon!', 'info');
        });
    });
});

// Remember Me Functionality
document.addEventListener('DOMContentLoaded', function() {
    const rememberCheckbox = document.querySelector('input[name="remember"]');
    
    if (rememberCheckbox) {
        // Check if user previously chose to be remembered
        const remembered = localStorage.getItem('rememberUser');
        if (remembered === 'true') {
            rememberCheckbox.checked = true;
        }
        
        rememberCheckbox.addEventListener('change', function() {
            if (this.checked) {
                localStorage.setItem('rememberUser', 'true');
            } else {
                localStorage.removeItem('rememberUser');
            }
        });
    }
});

// Auto-fill email if remembered
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.querySelector('input[name="email"]');
    const remembered = localStorage.getItem('rememberUser');
    
    if (emailInput && remembered === 'true') {
        const savedEmail = localStorage.getItem('savedEmail');
        if (savedEmail) {
            emailInput.value = savedEmail;
        }
    }
});

// Save email on successful login
function saveUserEmail(email) {
    const remembered = localStorage.getItem('rememberUser');
    if (remembered === 'true') {
        localStorage.setItem('savedEmail', email);
    }
}

// Form Auto-save (for registration forms)
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('form[action*="register"]');
    
    if (registerForm) {
        const inputs = registerForm.querySelectorAll('input, select');
        
        // Load saved data
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`form_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Save data on input
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                localStorage.setItem(`form_${this.name}`, this.value);
            });
        });
        
        // Clear saved data on successful submission
        registerForm.addEventListener('submit', function() {
            inputs.forEach(input => {
                localStorage.removeItem(`form_${input.name}`);
            });
        });
    }
});

// Session Management
function checkSessionStatus() {
    // This would typically make an AJAX call to check session status
    // For now, we'll just check if there are any session indicators in the DOM
    const loginElements = document.querySelectorAll('a[href*="login"]');
    const logoutElements = document.querySelectorAll('a[href*="logout"]');
    
    if (logoutElements.length > 0) {
        console.log('User appears to be logged in');
    } else if (loginElements.length > 0) {
        console.log('User appears to be logged out');
    }
}

// Initialize session check
document.addEventListener('DOMContentLoaded', checkSessionStatus);

// Logout confirmation
document.addEventListener('DOMContentLoaded', function() {
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = this.href;
            }
        });
    });
});
