// Worker Status Field Enhancement - Works with the new update system
document.addEventListener('DOMContentLoaded', function() {
    // Look for the Django-generated status field
    const statusField = document.querySelector('select[name="status"], input[name="status"]');
    
    if (statusField) {
        // Ensure status field is properly enabled
        statusField.removeAttribute('disabled');
        statusField.removeAttribute('readonly');
        statusField.style.pointerEvents = 'auto';
        statusField.style.opacity = '1';
        
        // Track original value for change detection
        const originalValue = statusField.value;
        
        // Enhanced change event listener
        statusField.addEventListener('change', function() {
            
            // Enhanced visual feedback
            this.style.borderColor = '#059669';
            this.style.borderWidth = '2px';
            this.style.transition = 'border-color 0.3s ease';
            
            // Add a subtle success animation
            this.classList.add('animate-pulse');
            
            setTimeout(() => {
                this.style.borderColor = '';
                this.style.borderWidth = '';
                this.classList.remove('animate-pulse');
            }, 2000);
            
            // Show a subtle feedback message
            if (typeof toast !== 'undefined') {
                toast.info(`Status changed to: ${this.value}`, 2000);
            }
        });
        
        // Ensure form submission includes status field
        const form = statusField.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                // Ensure status field is enabled for submission
                statusField.disabled = false;
                statusField.readOnly = false;
                
            });
        }
        
        // Add validation to prevent empty status
        statusField.addEventListener('blur', function() {
            if (!this.value || this.value.trim() === '') {
                this.style.borderColor = '#dc2626';
                this.style.borderWidth = '2px';
                
                if (typeof toast !== 'undefined') {
                    toast.error('Status is required');
                }
            }
        });
    }
}); 