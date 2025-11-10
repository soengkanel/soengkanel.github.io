

// //--------------validate worker infomation---------------------//
// var workerForm = document.getElementById("workerForm");
// var first_name = document.getElementById("id_first_name");

// // Initialize inline validation when DOM is loaded
// document.addEventListener('DOMContentLoaded', function() {
//     initializeInlineValidation();
    
//     // Ensure form exists before adding event listener
//     const form = document.getElementById("workerForm");
//     if (form) {
//         form.addEventListener('submit', (e) => onFormSubmit(e));
//         console.log('Form submit listener added successfully');
//     } else {
//         console.warn('Worker form not found - submit listener not added');
//     }
// });

// function onFormSubmit(e){
    
//     // For edit mode, use simplified validation
//     const isEditMode = document.getElementById('is_edit') && document.getElementById('is_edit').value === 'edit';
    
//     if (isEditMode) {
//         console.log('Edit mode: Using simplified validation');
        
//         // Clear any existing validation errors
//         clearAllValidationErrors();
        
//         // Only check for critical required fields in edit mode
//         const requiredFields = [
//             { field: document.getElementById('id_first_name'), name: 'First Name' },
//             { field: document.getElementById('id_last_name'), name: 'Last Name' },
//             { field: document.getElementById('id_status'), name: 'Status' }
//         ];
        
//         let hasErrors = false;
//         requiredFields.forEach(({ field, name }) => {
//             if (field && !field.value.trim()) {
//                 field.classList.add('is-invalid');
//                 setErrorStyle(field, `${name} is required`);
//                 hasErrors = true;
//             }
//         });
        
//         if (hasErrors) {
//             e.preventDefault();
//             if (typeof toast !== 'undefined') {
//                 toast.error('Please fill in all required fields');
//             }
//             return;
//         }
        
//         // Show loading state for edit mode
//         const editSubmitBtn = workerForm.querySelector('button[type="submit"]');
//         if (editSubmitBtn) {
//             editSubmitBtn.disabled = true;
//             editSubmitBtn.innerHTML = '<div class="flex items-center"><i class="fa fa-spinner fa-spin me-1"></i>Updating Worker...</div>';
//         }
        
//         console.log('Edit mode validation passed - submitting form');
//         return; // Let form submit normally
//     }
    
//     // For create mode, use simplified validation to avoid blocking
//     console.log('Create mode: Using simplified validation to prevent blocking');
    
//     // Clear any existing validation errors
//     clearAllValidationErrors();
    
//     // Only validate critical fields for create mode
//     const criticalFields = [
//         { field: document.getElementById('id_first_name'), name: 'First Name' },
//         { field: document.getElementById('id_last_name'), name: 'Last Name' },
//         { field: document.getElementById('id_sex'), name: 'Gender' },
//         { field: document.getElementById('id_dob'), name: 'Date of Birth' },
//         { field: document.getElementById('id_nationality'), name: 'Nationality' },
//         { field: document.getElementById('id_phone_number'), name: 'Phone Number' }
//     ];
    
//     let hasCreateErrors = false;
//     criticalFields.forEach(({ field, name }) => {
//         if (field && !field.value.trim()) {
//             field.classList.add('is-invalid');
//             setErrorStyle(field, `${name} is required`);
//             hasCreateErrors = true;
//         }
//     });
    
//     // Check photo requirement for create mode
//     const photoInput = document.getElementById('id_photo');
//     const capturedPhotoBlob = window.capturedPhotoBlob; // Check if photo was captured via camera
    
//     if (photoInput && (!photoInput.files || photoInput.files.length === 0) && !capturedPhotoBlob) {
//         setErrorStyle(photoInput, 'Worker photo is required');
//         hasCreateErrors = true;
//     }
    
//     if (hasCreateErrors) {
//         e.preventDefault();
//         if (typeof toast !== 'undefined') {
//             toast.error('Please fill in all required fields and add a photo');
//         }
//         scrollToFirstError();
//         return;
//     }
    
//     console.log('Create mode validation passed - submitting form');
    
//     // Show loading state for create mode
//     const createSubmitBtn = workerForm.querySelector('button[type="submit"]');
//     if (createSubmitBtn) {
//         createSubmitBtn.disabled = true;
//         createSubmitBtn.innerHTML = '<div class="flex items-center"><i class="fa fa-spinner fa-spin me-1"></i>Creating Worker...</div>';
//     }
// }

// function setErrorStyle(element, message) {
//     element.style.borderColor = 'red'; // Example: Red border
//     element.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.5)'; // Example: Red shadow
    



//     // Add an error message label
//     let errorLabel = document.getElementById(element.id + '-error');
//     if (!errorLabel) {
//         errorLabel = document.createElement('span');
//         errorLabel.id = element.id + '-error';
//         element.parentNode.insertBefore(errorLabel, element.nextSibling);
//     }
//     errorLabel.textContent = message;
//     errorLabel.style.color = 'red';
//     errorLabel.style.fontSize = '0.8em';
// }

// function clearErrorStyle(element) {
//     element.style.borderColor = ''; // Remove border color
//     element.style.boxShadow = ''; // Remove shadow

//     // Remove error message label if exists
//     const errorLabel = document.getElementById(element.id + '-error');
//     if (errorLabel) {
//         errorLabel.remove();
//     }
// }

// var fieldPhtoto = document.getElementById("id_photo")
// fieldPhtoto.addEventListener('change', (e)=>vaidateImageType(e, "Image type not allowed"))

// function vaidateImageType(e, message){

//     const allowedImageTypes = ['jpeg', 'jpg','png', 'gif', 'bmp'];
//     const selectedFile = e.target.files[0];
//     const extArr = selectedFile.name.split('.')
//     const extention = extArr[extArr.length - 1]


// }

// //-------------- Inline Validation System --------------//

// function initializeInlineValidation() {
//     // Get all form fields that need validation
//     const formFields = workerForm.querySelectorAll('input, select, textarea');
    
//     formFields.forEach(field => {
//         // Add event listeners for real-time validation
//         field.addEventListener('blur', (e) => validateField(e.target));
//         field.addEventListener('input', (e) => {
//             // Clear error immediately when user starts typing
//             if (hasError(e.target)) {
//                 clearErrorStyle(e.target);
//             }
//         });
//         field.addEventListener('change', (e) => validateField(e.target));
//     });
    
//     // Special handling for document formset fields
//     initializeDocumentValidation();
// }

// function validateField(field) {
//     const fieldName = field.name;
//     const fieldValue = field.value ? field.value.trim() : '';
//     const fieldType = field.type;
//     const isRequired = field.hasAttribute('required') || field.classList.contains('required');
    
//     // Clear previous error
//     clearErrorStyle(field);
    
//     // Skip validation for hidden fields
//     if (fieldType === 'hidden') return true;
    
//     // Required field validation
    
//     const selects = workerForm.querySelectorAll("select[required]");

//     selects.forEach(select => {

//         if (select.value === "") {
//             setErrorStyle(field, 'Please select an option.');

//         }
//       });

//     if (isRequired && !fieldValue) {
       
//         if (fieldType === 'select-one') {
//             alert("Select")
//             setErrorStyle(field, 'Please select an option.');
//         } else {
//             setErrorStyle(field, 'This field is required.');
//         }
//         return false;
//     }
    
//     // Specific field validations
//     switch (fieldName) {
//         case 'first_name':
//         case 'last_name':
//             return validateName(field, fieldValue);
//         case 'phone_number':
//             return validatePhoneNumber(field, fieldValue);
//         case 'dob':
//             return validateDateOfBirth(field, fieldValue);
//         case 'worker_id':
//             return validateWorkerId(field, fieldValue);
//         case 'nationality':
//             return validateNationality(field, fieldValue);
//         default:
//             // Generic validation for other required fields
//             if (isRequired && !fieldValue) {
//                 setErrorStyle(field, 'This field is required.');
//                 return false;
//             }
//     }
    
//     return true;
// }

// function validateName(field, value) {
//     if (!value) return true; // Required check is handled separately
    
//     if (value.length < 2) {
//         setErrorStyle(field, 'Name must be at least 2 characters long.');
//         return false;
//     }
    
//     if (value.length > 50) {
//         setErrorStyle(field, 'Name cannot exceed 50 characters.');
//         return false;
//     }
    
//     // Check for valid characters (letters, spaces, hyphens, apostrophes)
//     const namePattern = /^[a-zA-Z\s\-']+$/;
//     if (!namePattern.test(value)) {
//         setErrorStyle(field, 'Name can only contain letters, spaces, hyphens, and apostrophes.');
//         return false;
//     }
    
//     return true;
// }

// function validatePhoneNumber(field, value) {
//     if (!value) return true; // Required check is handled separately
    
//     // Remove all non-digit characters for validation
//     const cleanPhone = value.replace(/[^\d+]/g, '');
    
//     // Check if it's a valid Cambodia phone number format
//     const phonePattern = /^(\+?855|0)[0-9]{8,9}$/;
//     if (!phonePattern.test(cleanPhone)) {
//         setErrorStyle(field, 'Please enter a valid phone number (e.g., +855 12 345 6789 or 012 345 6789)');
//         return false;
//     }
    
//     return true;
// }

// function validateDateOfBirth(field, value) {
//     if (!value) return true; // Required check is handled separately
    
//     const dob = new Date(value);
//     const today = new Date();
    
//     // Check if date is valid
//     if (isNaN(dob.getTime())) {
//         setErrorStyle(field, 'Please enter a valid date.');
//         return false;
//     }
    
//     // Check if date is in the future
//     if (dob > today) {
//         setErrorStyle(field, 'Date of birth cannot be in the future.');
//         return false;
//     }
    
//     // Calculate age
//     const age = today.getFullYear() - dob.getFullYear() - 
//                 ((today.getMonth() < dob.getMonth() || 
//                  (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate())) ? 1 : 0);
    
//     if (age < 16) {
//         setErrorStyle(field, 'Worker must be at least 16 years old.');
//         return false;
//     }
    
//     if (age > 80) {
//         setErrorStyle(field, 'Please verify the date of birth. Age cannot exceed 80 years.');
//         return false;
//     }
    
//     return true;
// }

// function validateWorkerId(field, value) {
//     if (!value) return true; // Worker ID is optional (auto-generated if empty)
    
//     if (value.length < 3) {
//         setErrorStyle(field, 'Worker ID must be at least 3 characters long.');
//         return false;
//     }
    
//     if (value.length > 20) {
//         setErrorStyle(field, 'Worker ID cannot exceed 20 characters.');
//         return false;
//     }
    
//     // Character validation removed - allow any characters in Worker ID
    
//     return true;
// }

// function validateNationality(field, value) {
//     if (!value || value === '') {
//         setErrorStyle(field, 'Please select a nationality.');
//         return false;
//     }
//     return true;
// }

// function initializeDocumentValidation() {
//     // Add validation for document formset fields
//     const documentForms = document.querySelectorAll('.document-form');
    
//     documentForms.forEach((docForm, index) => {
//         const documentFields = docForm.querySelectorAll('input, select, textarea');
        
//         documentFields.forEach(field => {
//             // Skip Django formset management fields
//             if (field.type === 'hidden' || 
//                 field.name.includes('-id') || 
//                 field.name.includes('-DELETE') || 
//                 field.name.includes('TOTAL_FORMS') || 
//                 field.name.includes('INITIAL_FORMS')) {
//                 return; // Skip adding listeners to these fields
//             }
            
//             field.addEventListener('blur', (e) => validateDocumentField(e.target, index));
//             field.addEventListener('input', (e) => {
//                 if (hasError(e.target)) {
//                     clearErrorStyle(e.target);
//                 }
//             });
//             field.addEventListener('change', (e) => validateDocumentField(e.target, index));
//         });
//     });
// }

// function validateDocumentField(field, docIndex) {
//     const fieldName = field.name;
//     const fieldValue = field.value ? field.value.trim() : '';
//     const isRequired = field.hasAttribute('required') || field.classList.contains('required');
    
//     // Clear previous error
//     clearErrorStyle(field);
    
//     // Skip validation for hidden fields or Django formset management fields
//     if (field.type === 'hidden' || 
//         fieldName.includes('-id') || 
//         fieldName.includes('-DELETE') || 
//         fieldName.includes('TOTAL_FORMS') || 
//         fieldName.includes('INITIAL_FORMS')) {
//         return true;
//     }
    
//     // Check if this is a document field and validate accordingly
//     if (fieldName.includes('document_number')) {
//         return validateDocumentNumber(field, fieldValue, docIndex);
//     } else if (fieldName.includes('issue_date') || fieldName.includes('expiry_date')) {
//         return validateDocumentDate(field, fieldValue, fieldName);
//     } else if (fieldName.includes('issuing_authority')) {
//         return validateIssuingAuthority(field, fieldValue);
//     } else if (fieldName.includes('document_type')) {
//         return validateDocumentType(field, fieldValue);
//     } else if (fieldName.includes('document_file')) {
//         return validateDocumentFile(field, fieldValue, docIndex);
//     } else if (isRequired && !fieldValue) {
//         setErrorStyle(field, 'This field is required.');
//         return false;
//     }
    
//     return true;
// }

// function validateDocumentNumber(field, value, docIndex) {
//     if (!value) {
//         setErrorStyle(field, 'Document number is required.');
//         return false;
//     }
    
//     if (value.length < 3) {
//         setErrorStyle(field, 'Document number must be at least 3 characters long.');
//         return false;
//     }
    
//     if (value.length > 50) {
//         setErrorStyle(field, 'Document number cannot exceed 50 characters.');
//         return false;
//     }
    
//     return true;
// }

// function validateDocumentDate(field, value, fieldName) {
//     if (!value) {
//         setErrorStyle(field, 'Date is required.');
//         return false;
//     }
    
//     const date = new Date(value);
//     const today = new Date();
    
//     if (isNaN(date.getTime())) {
//         setErrorStyle(field, 'Please enter a valid date.');
//         return false;
//     }
    
//     if (fieldName.includes('expiry_date')) {
//         // Check if expiry date is after issue date
//         const issueField = field.form.querySelector('[name*="issue_date"]');
//         if (issueField && issueField.value) {
//             const issueDate = new Date(issueField.value);
//             if (date <= issueDate) {
//                 setErrorStyle(field, 'Expiry date must be after issue date.');
//                 return false;
//             }
//         }
//     }
    
//     return true;
// }

// function validateIssuingAuthority(field, value) {
//     if (!value) {
//         setErrorStyle(field, 'Issuing authority is required.');
//         return false;
//     }
    
//     if (value.length < 2) {
//         setErrorStyle(field, 'Issuing authority must be at least 2 characters long.');
//         return false;
//     }
    
//     if (value.length > 100) {
//         setErrorStyle(field, 'Issuing authority cannot exceed 100 characters.');
//         return false;
//     }
    
//     return true;
// }

// function validateDocumentType(field, value) {
//     if (!value || value === '') {
//         setErrorStyle(field, 'Please select a document type.');
//         return false;
//     }
//     return true;
// }

// function validateDocumentFile(field, value, docIndex) {
//     // SUPER SIMPLE: Only validate if absolutely no evidence of files exists
    
//     const documentForm = field.closest('.document-form');
    
//     // RULE 1: If document has an ID, it's existing - SKIP ALL VALIDATION
//     const documentIdField = documentForm.querySelector('input[name*="-id"]');
//     const hasDocumentId = documentIdField && documentIdField.value && documentIdField.value !== '';
    
//     if (hasDocumentId) {
//         return true; // Existing document, always pass
//     }
    
//     // RULE 2: Check if upload tracking field is true
//     const trackingField = documentForm.querySelector(`input[name*="-file_uploaded"]`);
//     const hasUploadTracking = trackingField && trackingField.value === 'true';
    
//     if (hasUploadTracking) {
//         return true; // File was uploaded, always pass
//     }
    
//     // RULE 3: Check if we have current files
//     const hasCurrentUpload = field.files && field.files.length > 0;
    
//     if (hasCurrentUpload) {
//         // Validate file properties and pass
//         return validateFileProperties(field.files[0], field);
//     }
    
//     // RULE 4: Check for any visible preview
//     const documentImage = documentForm.querySelector('.document-image');
//     const hasVisiblePreview = documentImage && 
//                              !documentImage.classList.contains('hidden') && 
//                              documentImage.style.display !== 'none' &&
//                              documentImage.src && 
//                              documentImage.src !== '';
    
//     if (hasVisiblePreview) {
//         return true; // Preview exists, file was uploaded
//     }
    
//     // ONLY fail if absolutely no evidence exists
//    // setErrorStyle(field, 'Document file is required for new documents.');
//     return false;
// }

// function validateFileProperties(file, field) {
//     // File size check (5MB max)
//     if (file.size > 5 * 1024 * 1024) {
//         setErrorStyle(field, 'File size cannot exceed 5MB.');
//         return false;
//     }
    
//     // File type check
//     const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'application/pdf'];
//     if (!allowedTypes.includes(file.type)) {
//         setErrorStyle(field, 'Please upload JPG, PNG, GIF, BMP, or PDF files only.');
//         return false;
//     }
    
//     return true;
// }

// function hasError(field) {
//     return field.style.borderColor === 'red' || field.style.borderColor === 'rgb(255, 0, 0)';
// }

// // Enhanced error styling with better UX
// function setErrorStyleEnhanced(element, message) {
//     // Apply error styling
//     element.style.borderColor = '#dc3545';
//     element.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
//     element.classList.add('is-invalid');
    
//     // Handle special cases
//     if (element.getAttribute('name') == 'photo') {

//         return;
//     }
    
//     // Find or create error message element
//     let errorLabel = document.getElementById(element.id + '-error');
//     if (!errorLabel) {
//         errorLabel = document.createElement('div');
//         errorLabel.id = element.id + '-error';
//         errorLabel.className = 'invalid-feedback';
//         errorLabel.style.display = 'block';
//         errorLabel.style.color = '#dc3545';
//         errorLabel.style.fontSize = '0.875rem';
//         errorLabel.style.marginTop = '0.25rem';
        
//         // Insert after the field or its wrapper
//         const wrapper = element.closest('.flex') || element.parentNode;
//         wrapper.appendChild(errorLabel);
//     }
    
//     errorLabel.textContent = message;
//     errorLabel.style.display = 'block';
// }

// function clearErrorStyleEnhanced(element) {
//     // Remove error styling
//     element.style.borderColor = '';
//     element.style.boxShadow = '';
//     element.classList.remove('is-invalid');
    
//     // Remove error message
//     const errorLabel = document.getElementById(element.id + '-error');
//     if (errorLabel) {
//         errorLabel.style.display = 'none';
//     }
    
//     // Handle photo error special case

// }

// // Comprehensive form validation function
// function validateAllFields() {
//     let isValid = true;
    
//     // Validate main form fields
//     const mainFields = workerForm.querySelectorAll('input:not([type="hidden"]), select, textarea');
//     mainFields.forEach(field => {
//         // Skip document formset fields (they have their own validation)
//         if (!field.name.includes('documents-')) {
//             if (!validateField(field)) {
//                 isValid = false;
//             }
//         }
//     });
    
//     // Validate document formset fields
//     const documentForms = document.querySelectorAll('.document-form');
//     documentForms.forEach((docForm, index) => {
//         const docFields = docForm.querySelectorAll('input, select, textarea');
//         docFields.forEach(field => {
//             // Skip Django formset management fields
//             if (field.type === 'hidden' || 
//                 field.name.includes('-id') || 
//                 field.name.includes('-DELETE') || 
//                 field.name.includes('TOTAL_FORMS') || 
//                 field.name.includes('INITIAL_FORMS')) {
//                 return; // Skip validation for these fields
//             }
            
//             if (!validateDocumentField(field, index)) {
//                 isValid = false;
//             }
//         });
//     });
    
//     return isValid;
// }

// // Clear all validation errors for edit mode
// function clearAllValidationErrors() {
//     // Remove all error styling
//     const errorElements = document.querySelectorAll('.is-invalid, [style*="border-color: red"]');
//     errorElements.forEach(element => {
//         element.classList.remove('is-invalid');
//         element.style.borderColor = '';
//         element.style.boxShadow = '';
//     });
    
//     // Remove all error messages
//     const errorLabels = document.querySelectorAll('[id$="-error"]');
//     errorLabels.forEach(label => {
//         label.remove();
//     });
    
//     // Hide photo error if exists

//     console.log('Cleared all validation errors for edit mode');
// }

// // Scroll to first error for better UX
// function scrollToFirstError() {
//     const firstError = document.querySelector('.is-invalid, [style*="border-color: red"]');
//     if (firstError) {
//         firstError.scrollIntoView({ 
//             behavior: 'smooth', 
//             block: 'center' 
//         });
        
//         // Focus on the field after scrolling
//         setTimeout(() => {
//             firstError.focus();
//         }, 500);
//     }
// }

// // Success styling for valid fields (optional enhancement)
// function setSuccessStyle(element) {
//     element.style.borderColor = '#198754';
//     element.style.boxShadow = '0 0 0 0.2rem rgba(25, 135, 84, 0.25)';
//     element.classList.add('is-valid');
//     element.classList.remove('is-invalid');
// }

// // Form section validation status (optional enhancement)
// function updateFormSectionStatus() {
//     const sections = document.querySelectorAll('.rounded-lg.border');
    
//     sections.forEach(section => {
//         const fields = section.querySelectorAll('input, select, textarea');
//         let hasErrors = false;
//         let allValid = true;
        
//         fields.forEach(field => {
//             if (hasError(field)) {
//                 hasErrors = true;
//                 allValid = false;
//             } else if (field.value && field.value.trim() !== '') {
//                 // Field has value but we need to check if it's valid
//                 if (!field.classList.contains('is-valid')) {
//                     allValid = false;
//                 }
//             } else {
//                 allValid = false;
//             }
//         });
        
//         // Update section styling
//         section.classList.remove('has-errors', 'is-valid');
//         if (hasErrors) {
//             section.classList.add('has-errors');
//         } else if (allValid && fields.length > 0) {
//             section.classList.add('is-valid');
//         }
//     });
// }



//--------------validate worker infomation---------------------//
var workerForm = document.getElementById("workerForm");
var first_name = document.getElementById("id_first_name");

var photoRequirements = document.getElementById("photo-requirements")

addEventListener("DOMContentLoaded", function () {

    const allInputsReq = workerForm.querySelectorAll('[required]');
    allInputsReq.forEach(input=>{

        input.addEventListener("change", function (e) {
            // alert("change")
            if(e.target.value !== ''){
                clearErrorStyle(input);
            }
        })
    })
});


workerForm.addEventListener('submit', (e)=>onFormSubmit(e));

function onFormSubmit(e){
    // First, determine if we're in edit mode or create mode
    const isEditMode = document.getElementById('is_edit') && document.getElementById('is_edit').value === 'edit';
    
    // ALWAYS prevent default first to ensure validation runs
    e.preventDefault();
    
    // Clear any previous validation errors first
    const allInputs = workerForm.querySelectorAll('input, select, textarea');
    allInputs.forEach(input => {
        clearErrorStyle(input);
    });

    // Check basic HTML5 validation first, but skip phone number and issuing authority
    const requiredInputs = workerForm.querySelectorAll('[required]');
    let firstErrorField = null;
    let hasValidationErrors = false;

    requiredInputs.forEach(input => {
        // Skip phone number and issuing authority fields - they are now optional
        if (input.id === 'id_phone_number' ||
            input.name === 'phone_number' ||
            input.id === 'id_issuing_authority' ||
            input.name === 'issuing_authority' ||
            input.name.includes('issuing_authority')) {
            // These fields are now optional, clear any required attribute
            input.removeAttribute('required');
            clearErrorStyle(input);
            return;
        }

        // Validate other required fields
        if(input.type === 'select-one' && input.value === ''){
            setErrorStyle(input, 'Please select an option.');
            if (!firstErrorField) firstErrorField = input;
            hasValidationErrors = true;
        } else if (input.value.trim() === '') {
            setErrorStyle(input, 'This field is required.');
            if (!firstErrorField) firstErrorField = input;
            hasValidationErrors = true;
        } else {
            clearErrorStyle(input);
        }
    });

    if(hasValidationErrors){
        // Focus on first error field for better UX
        if (firstErrorField) {
            firstErrorField.focus();
            firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Show a helpful message about the validation errors
        if (typeof toast !== 'undefined') {
            toast.error('Please fill in all required fields before submitting');
        }

        return; // Stop here if basic validation fails
    }
    
    // Now do custom validations only in create mode
    if (!isEditMode) {
        // Check age validation for DOB field
        const dobField = document.getElementById('id_dob');
        
        if (dobField && dobField.value) {
            // Calculate age directly here to ensure accuracy
            const birthDate = new Date(dobField.value);
            const today = new Date();
            
            // Check if birth date is valid
            if (isNaN(birthDate.getTime())) {
                setErrorStyle(dobField, 'Please enter a valid date of birth.');
                if (typeof toast !== 'undefined') {
                    toast.error('Please enter a valid date of birth');
                }
                return; // Stop submission
            }
            
            // Check if birth date is in the future
            if (birthDate > today) {
                setErrorStyle(dobField, 'Date of birth cannot be in the future.');
                if (typeof toast !== 'undefined') {
                    toast.error('Date of birth cannot be in the future');
                }
                return; // Stop submission
            }
            
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            const dayDiff = today.getDate() - birthDate.getDate();
            
            // Adjust age if birthday hasn't occurred yet this year
            if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
                age--;
            }
            
            if(age < 16){
                setErrorStyle(dobField, 'Worker must be at least 16 years old.');
                if (typeof toast !== 'undefined') {
                    toast.error('Worker must be at least 16 years old');
                }
                return; // Stop submission
            }
            
            if(age > 80){
                setErrorStyle(dobField, 'Please verify the date of birth. Age cannot exceed 80 years.');
                if (typeof toast !== 'undefined') {
                    toast.error('Please verify the date of birth. Age seems too high.');
                }
                return; // Stop submission
            }
        }
        
        // Check document date validation
        const documentForms = document.querySelectorAll('[id*="documents-"][id*="-issue_date"], [id*="documents-"][id*="-expiry_date"]');
        const documentErrors = [];
        
        // Group issue and expiry dates by form index
        const documentDates = {};
        documentForms.forEach(field => {
            const match = field.id.match(/documents-(\d+)-(issue_date|expiry_date)/);
            if (match) {
                const formIndex = match[1];
                const dateType = match[2];
                
                if (!documentDates[formIndex]) {
                    documentDates[formIndex] = {};
                }
                documentDates[formIndex][dateType] = field.value;
            }
        });
        
        // Validate each document form's dates
        for (const formIndex in documentDates) {
            const dates = documentDates[formIndex];
            const issueDate = dates.issue_date;
            const expiryDate = dates.expiry_date;
            
            if (issueDate && expiryDate) {
                const issue = new Date(issueDate);
                const expiry = new Date(expiryDate);
                
                if (expiry <= issue) {
                    const expiryField = document.getElementById(`id_documents-${formIndex}-expiry_date`);
                    const issueField = document.getElementById(`id_documents-${formIndex}-issue_date`);
                    
                    if (expiryField) setErrorStyle(expiryField, 'Expiry date must be after issue date');
                    if (issueField) setErrorStyle(issueField, 'Issue date must be before expiry date');
                    
                    documentErrors.push(`Document ${parseInt(formIndex) + 1}: Expiry date must be after issue date`);
                }
            }
        }
        
        if (documentErrors.length > 0) {
            if (typeof toast !== 'undefined') {
                toast.error('Please fix document date errors: ' + documentErrors.join(', '));
            }
            return; // Stop submission
        }
        
        // Check zone-building relationship validation
        const zoneField = document.getElementById('id_zone');
        const buildingField = document.getElementById('id_building');
        const floorField = document.getElementById('id_floor');
        
        if (zoneField && buildingField && zoneField.value && buildingField.value) {
            
            // Get buildings data from template
            const buildingsDataScript = document.getElementById('buildings-data');
            if (buildingsDataScript) {
                try {
                    const buildingsData = JSON.parse(buildingsDataScript.textContent);
                    const selectedBuilding = buildingsData.find(b => b.id == buildingField.value);
                    
                    if (selectedBuilding && selectedBuilding.zone_id != zoneField.value) {
                        setErrorStyle(buildingField, 'Selected building does not belong to the selected zone');
                        setErrorStyle(zoneField, 'Please select a zone that contains the selected building');
                        
                        if (typeof toast !== 'undefined') {
                            toast.error('Selected building does not belong to the selected zone');
                        }
                        return; // Stop submission
                    }
                } catch (e) {
                    // Could not validate zone-building relationship
                }
            }
        }
        
        // Check photo requirement for create mode
        const photoInput = document.getElementById('id_photo');
        const capturedPhotoBlob = window.capturedPhotoBlob; // Check if photo was captured via camera
        const currentPhotoDisplay = document.querySelector('.current-photo-display'); // Check if editing existing worker with photo
        const photoPreview = document.getElementById('photo-preview');
        const cameraPhotoPreview = document.getElementById('camera-photo-preview');
        
        // Check if photo is provided through any means
        const hasFileUpload = photoInput && photoInput.files && photoInput.files.length > 0;
        const hasCapturedPhoto = capturedPhotoBlob;
        const hasPhotoPreview = photoPreview && photoPreview.style.display !== 'none';
        const hasCameraPreview = cameraPhotoPreview && cameraPhotoPreview.style.display !== 'none';
        const hasCurrentPhoto = currentPhotoDisplay;
        
        if (!hasCurrentPhoto && !hasFileUpload && !hasCapturedPhoto && !hasPhotoPreview && !hasCameraPreview) {
            setErrorStyle(photoInput, 'Worker photo is required. Please upload a photo or use camera to capture one.');
            
            // Show the photo requirements div
            const photoRequirements = document.getElementById("photo-requirements");
            if (photoRequirements) {
                photoRequirements.classList.remove('hidden');
                const textErr = document.getElementById("text-err");
                if (textErr) {
                    textErr.textContent = "Photo is required for new workers";
                }
            }
            
            if (typeof toast !== 'undefined') {
                toast.error('Please upload or capture a worker photo before submitting');
            }
            
            // Scroll to photo field
            const photoSection = photoInput.closest('.col-span-1');
            if (photoSection) {
                photoSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            return; // Stop submission
        }
    }
    
    // All validation passed, now show loading state based on mode
    if (isEditMode) {
        // Show loading state for edit mode
        const editSubmitBtn = workerForm.querySelector('button[type="submit"]');
        if (editSubmitBtn) {
            editSubmitBtn.disabled = true;
            editSubmitBtn.innerHTML = '<div class="flex items-center">Updating Worker...</div>';
        }
    } else {
        // Create mode - validation has passed
        // Show loading state for create mode
        const createSubmitBtn = workerForm.querySelector('button[type="submit"]');
        if (createSubmitBtn) {
            createSubmitBtn.disabled = true;
            createSubmitBtn.innerHTML = '<div class="flex items-center"><i class="fa fa-spinner fa-spin me-1"></i>Creating Worker...</div>';
        }
    }
    
    // Now manually submit the form since we prevented default
    workerForm.submit();


}


function setErrorStyle(element, message) {
    element.style.borderColor = 'red'; // Example: Red border
    element.style.boxShadow = '0 0 5px rgba(255, 0, 0, 0.5)'; // Example: Red shadow
    
    if(element.getAttribute('name') == 'photo'){
        photoRequirements.classList.remove('hidden')
    }

    // Add an error message label
    let errorLabel = document.getElementById(element.id + '-error');
    if (!errorLabel) {
        errorLabel = document.createElement('span');
        errorLabel.id = element.id + '-error';
        element.parentNode.insertBefore(errorLabel, element.nextSibling);
    }
    errorLabel.textContent = message;
    errorLabel.style.color = 'red';
    errorLabel.style.fontSize = '0.8em';
}

function clearErrorStyle(element) {
    element.style.borderColor = ''; // Remove border color
    element.style.boxShadow = ''; // Remove shadow

    // Special handling for photo field
    if(element.getAttribute('name') == 'photo'){
        const photoRequirements = document.getElementById("photo-requirements");
        if (photoRequirements) {
            photoRequirements.classList.add('hidden');
        }
    }

    // Remove error message label if exists
    const errorLabel = document.getElementById(element.id + '-error');
    if (errorLabel) {
        errorLabel.remove();
    }
}

var fieldPhtoto = document.getElementById("id_photo")
if (fieldPhtoto) {
    fieldPhtoto.addEventListener('change', (e)=>vaidateImageType(e, "Image type not allowed"))
}

function vaidateImageType(e, message){
    if (!e.target.files || e.target.files.length === 0) {
        return; // No file selected
    }
    
    const allowedImageTypes = ['jpeg', 'jpg','png', 'gif', 'bmp'];
    const selectedFile = e.target.files[0];
    const extArr = selectedFile.name.split('.')
    const extention = extArr[extArr.length - 1].toLowerCase()
    let texterr = document.getElementById("text-err")
    
    if (allowedImageTypes.includes(extention)) {
        // Valid image type - clear any existing photo errors
        clearErrorStyle(e.target);
        photoRequirements.classList.add('hidden')
        if (texterr) {
            texterr.textContent = "The field is required";
        }
    } else {
        // Invalid image type
        if (texterr) {
            texterr.textContent = "Image type not allowed"
        }
        photoRequirements.classList.remove("hidden")
        setErrorStyle(e.target, "Invalid image type. Please select JPG, PNG, GIF, or BMP files.");
    }
}