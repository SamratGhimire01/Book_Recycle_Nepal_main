document.addEventListener('DOMContentLoaded', function() {
    const bookForm = document.getElementById('bookForm');
    if (!bookForm) return;

    // --- Get all DOM elements ---
    const dropZone = document.getElementById('dropZone');
    const actualFileInput = document.getElementById('actual-file-input');
    const uploadContent = document.getElementById('uploadContent');
    const imagePreviewsContainer = document.getElementById('imagePreviewsContainer');
    
    const previewBtn = document.getElementById('previewBtn');
    const previewCard = document.getElementById('previewCard');
    const previewImage = document.getElementById('previewImage');
    const previewTitle = document.getElementById('previewTitle');
    const previewCategory = document.getElementById('previewCategory');
    const previewPrice = document.getElementById('previewPrice');

    const MAX_IMAGES = 5;
    let uploadedFiles = [];

    // ===================================
    // == IMAGE UPLOAD LOGIC
    // ===================================
    dropZone.addEventListener('click', () => actualFileInput.click());
    actualFileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => { e.preventDefault(); e.stopPropagation(); }, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => dropZone.addEventListener(eventName, () => dropZone.classList.add('drop-zone--over')));
    ['dragleave', 'drop'].forEach(eventName => dropZone.addEventListener(eventName, () => dropZone.classList.remove('drop-zone--over')));
    dropZone.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files));

    function handleFiles(files) {
        if (uploadedFiles.length + files.length > MAX_IMAGES) {
            alert(`You can only upload up to ${MAX_IMAGES} images.`);
            return;
        }
        for (const file of files) {
            if (file.type.startsWith('image/')) {
                uploadedFiles.push(file);
            }
        }
        updatePreviews();
    }

    function updatePreviews() {
        imagePreviewsContainer.innerHTML = '';
        if (uploadedFiles.length > 0) {
            uploadContent.style.display = 'none';
        } else {
            uploadContent.style.display = 'block';
        }

        uploadedFiles.forEach((file, index) => {
            const previewWrapper = document.createElement('div');
            previewWrapper.className = 'image-preview';
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-image';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = (e) => { e.stopPropagation(); removeImage(index); };
            previewWrapper.appendChild(img);
            previewWrapper.appendChild(removeBtn);
            imagePreviewsContainer.appendChild(previewWrapper);
        });
        updateFileInput();
    }

    function removeImage(index) {
        uploadedFiles.splice(index, 1);
        updatePreviews();
    }

    function updateFileInput() {
        const dataTransfer = new DataTransfer();
        uploadedFiles.forEach(file => dataTransfer.items.add(file));
        actualFileInput.files = dataTransfer.files;
    }

    // ===================================
    // == LIVE PREVIEW LOGIC
    // ===================================
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            // Get current values from the form
            const title = document.getElementById('id_title').value;
            const categorySelect = document.getElementById('id_category');
            const categoryText = categorySelect.selectedIndex > 0 ? categorySelect.options[categorySelect.selectedIndex].text : '[Category]';
            const price = document.getElementById('id_price').value;

            // Update the preview card's content
            previewTitle.textContent = title || '[Book Title]';
            previewCategory.textContent = categoryText;
            previewPrice.textContent = price ? `Rs. ${price}` : 'Rs. [Price]';
            
            // Update the preview image
            if (uploadedFiles.length > 0) {
                previewImage.src = URL.createObjectURL(uploadedFiles[0]);
            } else {
                 previewImage.src = previewImage.dataset.placeholder || "{% static 'images/placeholder.png' %}";
            }

            // Show the preview card
            previewCard.classList.remove('hidden');
        });
    }

    // ===================================
    // == FORM SUBMISSION VALIDATION
    // ===================================
    bookForm.addEventListener('submit', function(e) {
        if (uploadedFiles.length === 0) {
            e.preventDefault();
            alert('Please upload at least one image of your book.');
            return;
        }
    });

});