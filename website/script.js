document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add scroll event listener for header
    const header = document.querySelector('header');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            header.classList.remove('scroll-up');
            return;
        }

        if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
            // Scroll Down
            header.classList.remove('scroll-up');
            header.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
            // Scroll Up
            header.classList.remove('scroll-down');
            header.classList.add('scroll-up');
        }
        lastScroll = currentScroll;
    });

    // Add animation to feature cards when they come into view
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .feature').forEach((el) => {
        observer.observe(el);
    });

    // Mobile menu functionality
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');

    mobileMenuButton.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.nav-links') && !e.target.closest('.mobile-menu-button')) {
            navLinks.classList.remove('active');
        }
    });

    // Close mobile menu when clicking a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });

    // Backend API URL
    const API_URL = 'http://localhost:5000';

    // Login form handling
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    // Store user data in localStorage
                    localStorage.setItem('user', JSON.stringify(data.user));
                    window.location.href = '/profile.html';
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred during login');
            }
        });
    }

    // Registration form handling
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const full_name = document.getElementById('full_name').value;
            const phone = document.getElementById('phone').value;
            const dob = document.getElementById('dob').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ full_name, phone, dob, username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    alert('Registration successful! Please login.');
                    window.location.href = '/login.html';
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred during registration');
            }
        });
    }

    // Check if user is logged in
    function checkAuth() {
        const user = localStorage.getItem('user');
        if (!user && !window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html')) {
            window.location.href = '/login.html';
        }
    }

    // Logout function
    function logout() {
        localStorage.removeItem('user');
        window.location.href = '/login.html';
    }

    // Check authentication on page load
    checkAuth();
}); 