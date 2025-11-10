// Worker Photo Handler - Improved photo handling for worker forms

class WorkerPhotoHandler {
    constructor() {
        this.initializePhotoHandling();
    }

    initializePhotoHandling() {
        // Handle photo input changes
        const photoInput = document.querySelector('input[type="file"][name="photo"]');
        if (photoInput) {
            photoInput.addEventListener('change', this.handlePhotoChange.bind(this));
        }

        // Handle photo error loading
        const existingPhotos = document.querySelectorAll('img[src*="serve_worker_photo"]');
        existingPhotos.forEach(img => {
            img.addEventListener('error', this.handlePhotoError.bind(this));
            img.addEventListener('load', this.handlePhotoLoad.bind(this));
        });
    }

    handlePhotoChange(event) {
        const file = event.target.files[0];
        const preview = document.getElementById('photo-preview');
        const previewImg = document.getElementById('photo-preview-img');
        const placeholder = document.getElementById('photo-placeholder');
        
        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
            if (!validTypes.includes(file.type)) {
                this.showError('Please select a valid image file (JPG, PNG, GIF, BMP)');
                // Don't clear the input - just show error
                return;
            }

            // Validate file size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                this.showError('Photo file too large. Maximum size is 5MB.');
                // Don't clear the input - just show error
                return;
            }

            // Clear any previous errors
            this.hideError();

            // Show preview
            const reader = new FileReader();
            reader.onload = (e) => {
                if (previewImg) {
                    previewImg.src = e.target.result;
                }
                if (preview) {
                    preview.style.display = 'block';
                }
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
                this.hideError();
            };
            reader.readAsDataURL(file);
        } else {
            // No file selected, hide preview
            if (preview) {
                preview.style.display = 'none';
            }
            if (placeholder) {
                placeholder.style.display = 'block';
            }
        }
    }

    handlePhotoError(event) {
        // Hide the broken image
        event.target.style.display = 'none';
        
        // Show placeholder if available
        const placeholder = document.getElementById('photo-placeholder');
        if (placeholder) {
            placeholder.style.display = 'block';
        }

        // Show error message
        this.showError('Failed to load existing photo. You may need to upload a new one.');
    }

    handlePhotoLoad(event) {
        this.hideError();
    }

    showError(message) {
        const errorElement = document.getElementById('photo-error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
            errorElement.style.display = 'block';
        }
    }

    hideError() {
        const errorElement = document.getElementById('photo-error');
        if (errorElement) {
            errorElement.classList.add('hidden');
            errorElement.style.display = 'none';
        }
    }

    // Method to refresh photo display after form submission
    refreshPhotoDisplay(workerId) {
        const existingPhotos = document.querySelectorAll('img[src*="serve_worker_photo"]');
        existingPhotos.forEach(img => {
            const currentSrc = img.src;
            const timestamp = new Date().getTime();
            
            // Add timestamp to force refresh
            if (currentSrc.includes('?')) {
                img.src = currentSrc.split('?')[0] + '?t=' + timestamp;
            } else {
                img.src = currentSrc + '?t=' + timestamp;
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new WorkerPhotoHandler();
});

// Export for use in other scripts
window.WorkerPhotoHandler = WorkerPhotoHandler;