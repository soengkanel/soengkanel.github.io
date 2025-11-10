/**
 * Inline validation for worker forms
 * Provides real-time validation feedback for better UX
 */

class WorkerFormValidator {
    constructor() {
        this.form = document.getElementById('worker-form');
        this.documentForms = [];
        this.validationRules = {
            required: this.validateRequired,
            email: this.validateEmail,
            phone: this.validatePhone,
            dateRange: this.validateDateRange,
            futureDate: this.validateFutureDate,
            pastDate: this.validatePastDate
        };
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        // Initialize validation for main form fields
        this.initMainFormValidation();
        
        // Initialize validation for document forms
        this.initDocumentValidation();
        
        // Prevent form submission if validation fails
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showValidationSummary();
            }
        });
    }
    
    initMainFormValidation() {
        // First name validation
        const firstName = this.form.querySelector('[name="first_name"]');
        if (firstName) {
            this.addInlineValidation(firstName, 'required', 'First name is required');
        }
        
        // Last name validation
        const lastName = this.form.querySelector('[name="last_name"]');
        if (lastName) {
            this.addInlineValidation(lastName, 'required', 'Last name is required');
        }
        
        // Email validation
        const email = this.form.querySelector('[name="email"]');
        if (email) {
            this.addInlineValidation(email, 'email', 'Please enter a valid email address');
        }
        
        // Phone validation
        const phone = this.form.querySelector('[name="phone_number"]');
        if (phone) {
            this.addInlineValidation(phone, 'phone', 'Please enter a valid phone number');
        }
        
        // Date of birth validation (must be past date)
        const dob = this.form.querySelector('[name="date_of_birth"]');
        if (dob) {
            this.addInlineValidation(dob, 'pastDate', 'Date of birth must be in the past');
        }
    }
    
    initDocumentValidation() {
        // Find all document forms - using the actual class from the template
        const documentSections = document.querySelectorAll('.document-formset-row, .document-form');
        
        documentSections.forEach((section, index) => {
            this.validateDocumentSection(section, index);
        });
        
        // Watch for new document forms being added
        this.observeDocumentChanges();
    }
    
    validateDocumentSection(section, index) {
        const documentType = section.querySelector('[name$="-document_type"]');
        const issueDate = section.querySelector('[name$="-issue_date"]');
        const expiryDate = section.querySelector('[name$="-expiry_date"]');
        const documentNumber = section.querySelector('[name$="-document_number"]');
        
        // Document number validation
        if (documentNumber && documentType) {
            documentNumber.addEventListener('blur', () => {
                if (documentType.value && !documentNumber.value) {
                    this.showFieldError(documentNumber, 'Document number is required');
                } else {
                    this.clearFieldError(documentNumber);
                }
            });
        }
        
        // Issue and expiry date validation
        if (issueDate && expiryDate) {
            // Validate issue date is not in future
            issueDate.addEventListener('change', () => {
                const today = new Date();
                const issueValue = new Date(issueDate.value);
                
                if (issueValue > today) {
                    this.showFieldError(issueDate, 'Issue date cannot be in the future');
                } else {
                    this.clearFieldError(issueDate);
                    // Re-validate expiry date if it exists
                    if (expiryDate.value) {
                        this.validateExpiryDate(issueDate, expiryDate);
                    }
                }
            });
            
            // Validate expiry date is after issue date
            expiryDate.addEventListener('change', () => {
                this.validateExpiryDate(issueDate, expiryDate);
            });
        }
    }
    
    validateExpiryDate(issueDate, expiryDate) {
        if (!issueDate.value || !expiryDate.value) {
            this.clearFieldError(expiryDate);
            return;
        }
        
        const issueValue = new Date(issueDate.value);
        const expiryValue = new Date(expiryDate.value);
        
        if (expiryValue <= issueValue) {
            this.showFieldError(expiryDate, 'Expiry date must be after issue date');
        } else {
            this.clearFieldError(expiryDate);
        }
    }
    
    addInlineValidation(field, validationType, errorMessage) {
        // Add validation on blur
        field.addEventListener('blur', () => {
            if (!this.validationRules[validationType].call(this, field)) {
                this.showFieldError(field, errorMessage);
            } else {
                this.clearFieldError(field);
            }
        });
        
        // Clear error on input
        field.addEventListener('input', () => {
            if (field.classList.contains('is-invalid')) {
                if (this.validationRules[validationType].call(this, field)) {
                    this.clearFieldError(field);
                }
            }
        });
    }
    
    showFieldError(field, message) {
        // Remove any existing error
        this.clearFieldError(field);
        
        // Add invalid class
        field.classList.add('is-invalid');
        
        // Create and insert error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Insert after the field
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
        
        // Add visual indicator
        field.style.borderColor = '#dc3545';
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        field.style.borderColor = '';
        
        // Remove error message if exists
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    // Validation rules
    validateRequired(field) {
        return field.value.trim() !== '';
    }
    
    validateEmail(field) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return !field.value || emailRegex.test(field.value);
    }
    
    validatePhone(field) {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        return !field.value || (field.value.length >= 7 && phoneRegex.test(field.value));
    }
    
    validateFutureDate(field) {
        if (!field.value) return true;
        const date = new Date(field.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return date > today;
    }
    
    validatePastDate(field) {
        if (!field.value) return true;
        const date = new Date(field.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return date <= today;
    }
    
    validateDateRange(startField, endField) {
        if (!startField.value || !endField.value) return true;
        const startDate = new Date(startField.value);
        const endDate = new Date(endField.value);
        return endDate > startDate;
    }
    
    validateForm() {
        let isValid = true;
        const errors = [];
        
        // Validate all required fields
        const requiredFields = this.form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!this.validateRequired(field)) {
                const label = field.closest('.mb-2')?.querySelector('label')?.textContent || field.name;
                errors.push(`${label} is required`);
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Validate all document dates
        const documentSections = document.querySelectorAll('.document-form');
        documentSections.forEach((section, index) => {
            const issueDate = section.querySelector('[name$="-issue_date"]');
            const expiryDate = section.querySelector('[name$="-expiry_date"]');
            
            if (issueDate && expiryDate && issueDate.value && expiryDate.value) {
                const issueValue = new Date(issueDate.value);
                const expiryValue = new Date(expiryDate.value);
                
                if (expiryValue <= issueValue) {
                    errors.push(`Document ${index + 1}: Expiry date must be after issue date`);
                    this.showFieldError(expiryDate, 'Expiry date must be after issue date');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }
    
    showValidationSummary() {
        // Scroll to first error
        const firstError = this.form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    observeDocumentChanges() {
        // Watch for new document forms being added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList?.contains('document-form')) {
                        const index = document.querySelectorAll('.document-form').length - 1;
                        this.validateDocumentSection(node, index);
                    }
                });
            });
        });
        
        const container = document.getElementById('document-forms-container');
        if (container) {
            observer.observe(container, { childList: true, subtree: true });
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    new WorkerFormValidator();
});

// Export for use in other scripts
window.WorkerFormValidator = WorkerFormValidator;