// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {

    // ===================================
    // == 1. SETUP & GLOBAL VARIABLES
    // ===================================
    const mainJsScript = document.getElementById('main-js');
    const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfTokenInput ? csrfTokenInput.value : null;

    // --- Get all dynamic URLs from <script> in base.html ---
    const toggleFavoriteUrl = mainJsScript ? mainJsScript.dataset.toggleFavoriteUrl : null;
    const liveSearchUrl = mainJsScript ? mainJsScript.dataset.liveSearchUrl : null;
    const toggleFollowUrl = mainJsScript ? mainJsScript.dataset.toggleFollowUrl : null;
    const addToCartUrl = mainJsScript ? mainJsScript.dataset.addToCartUrl : null;
    const removeFromCartUrl = mainJsScript ? mainJsScript.dataset.removeFromCartUrl : null;
    const viewCartUrl = mainJsScript ? mainJsScript.dataset.viewCartUrl : null;

    // ===================================
    // == 2. DARK MODE
    // ===================================
    const darkModeToggle = document.getElementById('darkModeToggle');
    const bodyElement = document.body;
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', bodyElement.classList.contains('dark-mode') ? 'enabled' : 'disabled');
        });
    }

    // ===================================
    // == 3. MOBILE MENU & HELPERS
    // ===================================
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
    }

    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) backToTopBtn.classList.add('visible');
            else backToTopBtn.classList.remove('visible');
        });
        backToTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId.length > 1) {
                e.preventDefault();
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                        mobileMenu.classList.add('hidden');
                    }
                }
            }
        });
    });

    // ===================================
    // == 4. FAVORITES
    // ===================================
    if (toggleFavoriteUrl && csrfToken) {
        document.querySelectorAll('.toggle-favorite-form').forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const button = this.querySelector('.bc-heart-icon');

                fetch(toggleFavoriteUrl, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': csrfToken }
                })
                .then(response => {
                    if (!response.ok) {
                        window.location.href = '/login/'; 
                        return Promise.reject('User not logged in');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'favorited') {
                        button.classList.add('is-favorite');
                    } else if (data.status === 'unfavorited') {
                        button.classList.remove('is-favorite');
                    }
                })
                .catch(error => console.error('Favorite toggle error:', error));
            });
        });
    }

    // ===================================
    // == 5. LIVE SEARCH
    // ===================================
    const searchInput = document.getElementById('liveSearchInput');
    const searchResults = document.getElementById('searchResults');
    if (searchInput && searchResults && liveSearchUrl) {
        searchInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length > 2) {
                fetch(`${liveSearchUrl}?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    if (data.results.length > 0) {
                        searchResults.style.display = 'block';
                        data.results.forEach(book => {
                            const item = document.createElement('a');
                            item.href = book.url;
                            item.className = 'search-result-item';
                            item.innerHTML = `<img src="${book.image_url || '/static/images/placeholder.png'}"><span>${book.title}</span>`;
                            searchResults.appendChild(item);
                        });
                    } else {
                        searchResults.style.display = 'none';
                    }
                });
            } else {
                searchResults.style.display = 'none';
            }
        });

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // ===================================
    // == 6. FOLLOW / UNFOLLOW
    // ===================================
    const followForm = document.getElementById('followForm');
    if (followForm && csrfToken && toggleFollowUrl) {
        followForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const followBtn = document.getElementById('followBtn');

            fetch(toggleFollowUrl, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': csrfToken }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    if (data.is_following) {
                        followBtn.textContent = 'Unfollow';
                        followBtn.classList.remove('btn-primary-profile');
                        followBtn.classList.add('btn-secondary-profile');
                    } else {
                        followBtn.textContent = 'Follow';
                        followBtn.classList.remove('btn-secondary-profile');
                        followBtn.classList.add('btn-primary-profile');
                    }
                } else {
                    console.error('Failed to toggle follow status:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    if (addToCartUrl && csrfToken) {
        document.querySelectorAll('.add-to-cart-form').forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const button = this.querySelector('button');
                const originalText = button.textContent;
                button.textContent = "Adding...";
                button.disabled = true;

                try {
                    const response = await fetch(addToCartUrl, {
                        method: 'POST',
                        body: new FormData(this),
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    
                    if (!response.ok) { window.location.href = '/login/'; return; }
                    
                    const data = await response.json();
                    
                    if (data.status === 'ok') {
                        button.textContent = "Added!";
                        
                        // --- THIS IS THE FIX ---
                        // Update the counter directly with the number from the server's response.
                        updateCartCounter(data.cart_item_count);
                        
                        // You can still alert the user or show a small pop-up message here
                        // alert(data.message);
                    } else {
                        button.textContent = originalText;
                    }
                } catch (error) {
                    console.error("Add to cart failed:", error);
                    button.textContent = originalText;
                } finally {
                    setTimeout(() => {
                        button.disabled = false;
                        // Keep the "Added!" text to show the item is in the cart
                    }, 2000);
                }
            });
        });
    }

    // You still need the updateCartCounter function for this to work
    function updateCartCounter(count) {
        if (cartCounter) {
            cartCounter.textContent = count;
            cartCounter.style.display = count > 0 ? 'flex' : 'none';
        }
    }
 // ===================================
    // == 8. CART PAGE INTERACTIVITY
    // ===================================
    const cartPage = document.querySelector('.cart-page-container');
    if (cartPage) {
        const checkboxes = document.querySelectorAll('.item-checkbox');
        const subtotalDisplay = document.getElementById('subtotalDisplay');
        const deliveryDisplay = document.getElementById('deliveryDisplay');
        const grandTotalDisplay = document.getElementById('grandTotalDisplay');
        const itemCountDisplay = document.getElementById('itemCount');
        const initialSubtotal = parseFloat(subtotalDisplay.textContent.replace('Rs.', ''));
        const deliveryCharge = parseFloat(deliveryDisplay.textContent.replace('Rs.', ''));

        function updateTotals() {
            let currentSubtotal = 0;
            let checkedItemCount = 0;
            checkboxes.forEach(box => {
                if (box.checked) {
                    currentSubtotal += parseFloat(box.dataset.price);
                    checkedItemCount++;
                }
            });
            const grandTotal = currentSubtotal + deliveryCharge; // Simplified for now
            subtotalDisplay.textContent = `Rs. ${currentSubtotal.toFixed(2)}`;
            grandTotalDisplay.textContent = `Rs. ${grandTotal.toFixed(2)}`;
            itemCountDisplay.textContent = checkedItemCount;
        }

        checkboxes.forEach(box => {
            box.addEventListener('change', updateTotals);
        });
        
        // Remove from cart logic
        document.querySelectorAll('.remove-from-cart-form').forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                
                try {
                    const response = await fetch(removeFromCartUrl, {
                        method: 'POST',
                        body: formData,
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    if (!response.ok) throw new Error('Failed to remove');
                    
                    // If successful, simply reload the page to show the updated cart
                    window.location.reload();

                } catch (error) {
                    console.error("Remove from cart failed:", error);
                }
            });
        });
    }


    
}); // End DOMContentLoaded
