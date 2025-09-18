// static/js/cart.js

document.addEventListener('DOMContentLoaded', function() {
    // --- SETUP: Get URLs and the CSRF token ---
    const cartScriptTag = document.getElementById('cart-script');
    if (!cartScriptTag) return; // Exit if not on the cart page

    const updateSelectionUrl = cartScriptTag.dataset.updateSelectionUrl;
    const checkoutUrl = cartScriptTag.dataset.checkoutUrl;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Get all the elements we need to interact with
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const subtotalDisplay = document.getElementById('subtotalDisplay');
    const grandTotalDisplay = document.getElementById('grandTotalDisplay');
    const deliveryDisplay = document.getElementById('deliveryDisplay');
    const itemCountDisplay = document.getElementById('itemCount');
    const checkoutBtn = document.getElementById('checkoutBtn');

    // --- CORE FUNCTION to calculate totals based on checked boxes ---
    function calculateAndUpdateTotals() {
        let currentSubtotal = 0;
        let selectedItemCount = 0;

        checkboxes.forEach(box => {
            if (box.checked) {
                currentSubtotal += parseFloat(box.dataset.price);
                selectedItemCount++;
            }
        });

        const deliveryCharge = 100.00; // Placeholder value
        const grandTotal = currentSubtotal + deliveryCharge;

        // Update the text on the page
        if (subtotalDisplay) subtotalDisplay.textContent = `Rs. ${currentSubtotal.toFixed(2)}`;
        if (grandTotalDisplay) grandTotalDisplay.textContent = `Rs. ${grandTotal.toFixed(2)}`;
        if (itemCountDisplay) itemCountDisplay.textContent = selectedItemCount;
    }

    // --- EVENT LISTENERS ---

    // 1. Listen for changes on any checkbox and recalculate the total.
    checkboxes.forEach(box => {
        box.addEventListener('change', calculateAndUpdateTotals);
    });

    // 2. Listen for a click on the "Proceed to Checkout" button.
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            const selectedBookIds = [];
            document.querySelectorAll('.item-checkbox:checked').forEach(box => {
                selectedBookIds.push(box.dataset.bookId);
            });

            if (selectedBookIds.length === 0) {
                alert('Please select at least one item to proceed to checkout.');
                return; // Stop the function
            }
            
            // Disable the button to prevent multiple clicks
            checkoutBtn.disabled = true;
            checkoutBtn.textContent = 'Processing...';

            // Prepare the data to send to the server
            const formData = new FormData();
            selectedBookIds.forEach(id => formData.append('selected_ids[]', id));
            
            // Send the list of selected IDs to the server to be saved in the session
            fetch(updateSelectionUrl, {
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': csrfToken }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // If the save was successful, NOW redirect to the actual checkout page
                    window.location.href = checkoutUrl;
                } else {
                    alert('Something went wrong. Please try again.');
                    checkoutBtn.disabled = false; // Re-enable the button
                    checkoutBtn.textContent = 'Proceed to Checkout';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                checkoutBtn.disabled = false;
                checkoutBtn.textContent = 'Proceed to Checkout';
            });
        });
    }

    // --- INITIAL CALCULATION ---
    // Run the calculation once when the page first loads to set the initial state.
    calculateAndUpdateTotals();
});