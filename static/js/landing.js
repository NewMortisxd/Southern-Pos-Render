/* ============================================
   LEMON POS - LANDING PAGE JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // NAVBAR SCROLL EFFECT
    // ============================================
    const navbar = document.querySelector('.navbar-scroll');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking on a link
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('active');
            });
        });
    }

    // ============================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if href is just "#"
            if (href === '#') {
                e.preventDefault();
                return;
            }

            const targetElement = document.querySelector(href);
            
            if (targetElement) {
                e.preventDefault();
                const offsetTop = targetElement.offsetTop - 80;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ============================================
    // INTERSECTION OBSERVER FOR FADE-IN ANIMATIONS
    // ============================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe all elements with fade-in class
    document.querySelectorAll('.fade-in').forEach(element => {
        observer.observe(element);
    });

    // ============================================
    // ANIMATED COUNTER FOR STATS
    // ============================================
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start).toLocaleString();
            }
        }, 16);
    }

    // Trigger counter animation when stats section is visible
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counters = entry.target.querySelectorAll('.stat-number');
                    counters.forEach(counter => {
                        const target = parseInt(counter.getAttribute('data-target'));
                        animateCounter(counter, target);
                    });
                    statsObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        statsObserver.observe(statsSection);
    }

    // ============================================
    // DEMO TAB SWITCHING (if implemented)
    // ============================================
    const demoButtons = document.querySelectorAll('.demo-tab-btn');
    const demoImages = document.querySelectorAll('.demo-image');

    demoButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and images
            demoButtons.forEach(btn => btn.classList.remove('active'));
            demoImages.forEach(img => img.classList.remove('active'));

            // Add active class to clicked button and corresponding image
            button.classList.add('active');
            if (demoImages[index]) {
                demoImages[index].classList.add('active');
            }
        });
    });

    // ============================================
    // PRICING TOGGLE (Monthly/Yearly) - if needed
    // ============================================
    const pricingToggle = document.getElementById('pricing-toggle');
    if (pricingToggle) {
        pricingToggle.addEventListener('change', function() {
            const prices = document.querySelectorAll('.price-amount');
            prices.forEach(price => {
                const monthly = price.getAttribute('data-monthly');
                const yearly = price.getAttribute('data-yearly');
                
                if (this.checked) {
                    price.textContent = yearly;
                } else {
                    price.textContent = monthly;
                }
            });
        });
    }

    // ============================================
    // FORM VALIDATION (if contact form exists)
    // ============================================
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            const name = this.querySelector('input[name="name"]').value;
            
            if (email && name) {
                // Show success message
                alert('¡Gracias por tu interés! Te contactaremos pronto.');
                this.reset();
            }
        });
    }

    // ============================================
    // LAZY LOADING IMAGES
    // ============================================
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));

    // ============================================
    // PREVENT FLASH OF UNSTYLED CONTENT
    // ============================================
    document.body.style.opacity = '1';

    // ============================================
    // CONSOLE EASTER EGG
    // ============================================
    console.log('%c🍋 Lemon POS', 'color: #22c55e; font-size: 24px; font-weight: bold;');
    console.log('%c¿Buscando algo? Únete a nuestro equipo: contacto@lemonpos.com', 'color: #666; font-size: 12px;');
});
