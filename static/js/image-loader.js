/**
 * Modern Football Image Loader
 * Provides lazy loading, shimmer placeholders, and fallback images
 */

class FootballImageLoader {
    constructor() {
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupImages());
        } else {
            this.setupImages();
        }
    }

    setupImages() {
        // Find all images with data-football-img attribute
        const images = document.querySelectorAll('[data-football-img]');
        
        images.forEach(img => {
            this.enhanceImage(img);
        });

        // Setup intersection observer for lazy loading
        this.setupLazyLoading();
    }

    enhanceImage(img) {
        const src = img.getAttribute('data-src') || img.src;
        const fallbackSrc = img.getAttribute('data-fallback') || '/static/images/placeholder.png';
        
        // Create container if not already wrapped
        if (!img.parentElement.classList.contains('image-container')) {
            const container = document.createElement('div');
            container.className = 'image-container';
            img.parentNode.insertBefore(container, img);
            container.appendChild(img);
            
            // Add shimmer placeholder
            const shimmer = document.createElement('div');
            shimmer.className = 'shimmer-placeholder';
            container.insertBefore(shimmer, img);
        }

        // Add football-image class
        img.classList.add('football-image', 'hidden');
        
        // Handle image load
        img.addEventListener('load', () => {
            img.classList.remove('hidden');
            img.classList.add('loaded');
            const shimmer = img.parentElement.querySelector('.shimmer-placeholder');
            if (shimmer) {
                shimmer.style.display = 'none';
            }
        });

        // Handle image error with fallback
        img.addEventListener('error', () => {
            if (img.src !== fallbackSrc) {
                img.src = fallbackSrc;
            } else {
                // If fallback also fails, show placeholder
                img.style.display = 'none';
                const shimmer = img.parentElement.querySelector('.shimmer-placeholder');
                if (shimmer) {
                    shimmer.innerHTML = '⚽';
                    shimmer.style.display = 'flex';
                    shimmer.style.alignItems = 'center';
                    shimmer.style.justifyContent = 'center';
                    shimmer.style.fontSize = '3rem';
                }
            }
        });

        // Set lazy loading
        img.loading = 'lazy';
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }
}

// Initialize on page load
const imageLoader = new FootballImageLoader();

// Export for use in other scripts
window.FootballImageLoader = FootballImageLoader;
