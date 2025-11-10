//---------------------- document upload scanner----------------------//
let formIndex = parseInt(document.querySelector('#id_documents-TOTAL_FORMS').value);
var addDocumentBtn = document.getElementById('btnAddDocForm');

addEventListener('DOMContentLoaded', function(){
    // Clear localStorage for create mode to prevent stale document previews
    const isEditMode = document.getElementById('is_edit') && document.getElementById('is_edit').value === 'edit';
    const formWasSubmitted = document.getElementById('form-action') && document.getElementById('form-action').value === 'submited';
    
    if (!isEditMode && !formWasSubmitted) {
        // Clear any stale document preview data for create mode
        cleanupAllDocumentStorage();
        
        // Also clear any visible previews that might be showing
        clearAllVisiblePreviews();
    }
    
    initializeDocumentPreviews();
    // Check for document type conflicts on page load
    setTimeout(() => checkDocumentTypeReplacement(), 200);
    
    // Setup Add Document button functionality
    setupAddDocumentButton();
})

function initializeDocumentPreviews() {
    // Initialize previews for all existing document forms
    const documentForms = document.querySelectorAll('.document-form');
    
    documentForms.forEach((form, index) => {
        const fileInput = form.querySelector(`input[type="file"][name*="document_file"]`);
        const docTypeSelect = form.querySelector(`select[name*="document_type"]`);
        
        if (fileInput) {
            // Add change listener for new uploads
            fileInput.addEventListener('change', function(e) {
                // docTypeSelect.value = 'passport'
                handleDocumentPreview(e, index);
                checkDocumentTypeReplacement();
            });
            
            // ALWAYS remove required attribute - we handle validation in JavaScript
            fileInput.removeAttribute('required');
        }
        
        if (docTypeSelect) {
            // Add change listener for document type changes
            docTypeSelect.addEventListener('change', function(e) {
             
                if(e.target.value !='passport' && e.target.value !='id_card'){
         
                    if(e.target.value =='id_card'){
                        e.target.value = 'id_card'
                    }else if(e.target.value =='passport'){
                        e.target.value = 'passport'
                    }else{
                        e.target.value = ""
                    }
                }
                checkDocumentTypeReplacement();
            });
        }
        
        // Check if this document already has evidence of a file
        const hasExistingEvidence = checkForExistingFileEvidence(form, index);
        if (hasExistingEvidence) {
            // Mark tracking fields appropriately
            const trackingField = form.querySelector(`input[name*="-file_uploaded"]`);
            if (trackingField) {
                trackingField.value = 'true';
            }
            sessionStorage.setItem(`doc-${index}-had-file`, 'true');
            fileInput.setAttribute('data-has-file', 'true');
        }
        
        // Only restore preview from localStorage in edit mode or after validation failures
        // Check if we're in create mode vs edit mode or form was submitted
        const isEditMode = document.getElementById('is_edit') && document.getElementById('is_edit').value === 'edit';
        const formWasSubmitted = document.getElementById('form-action') && document.getElementById('form-action').value === 'submited';
        
        if (isEditMode || formWasSubmitted) {
            restorePreviewFromStorage(index);
        }
    });
}

function checkForExistingFileEvidence(form, index) {
    // Check multiple sources for evidence of existing files
    const sources = [
        // Server-provided preview
        form.querySelector('.doc-img-preview'),
        // File existence indicator
        form.querySelector('.text-success'),
        // Document ID (existing document)
        form.querySelector('input[name*="-id"]')?.value,
        // localStorage
        localStorage.getItem(`docFile-${index}`),
        // sessionStorage
        sessionStorage.getItem(`doc-${index}-had-file`)
    ];
    
    return sources.some(source => {
        if (typeof source === 'string') {
            return source && source.trim() !== '' && source !== 'false';
        }
        return !!source;
    });
}

function restorePreviewFromStorage(formIndex) {
    const documentImage = document.getElementById(`document-image-${formIndex}`);
    const documentImageIcon = document.getElementById(`document-image-icon-${formIndex}`);
    const fileUploadedField = document.getElementById(`file-uploaded-${formIndex}`);
    
    if (!documentImage || !documentImageIcon) return;
    
    // ENHANCED RESTORATION: Check multiple sources
    
    // 1. Check localStorage
    const storedFile = localStorage.getItem(`docFile-${formIndex}`);
    
    // 2. Check if tracking field already indicates upload
    const alreadyTracked = fileUploadedField && fileUploadedField.value === 'true';
    
    // 3. Check if there's already a preview showing (from server)
    const hasServerPreview = documentImage.src && 
                            !documentImage.classList.contains('hidden') && 
                            documentImage.style.display !== 'none' &&
                            !documentImage.src.includes('data:image/svg+xml');
    
    if (storedFile) {
        try {
            // Restore from localStorage
            documentImage.src = storedFile;
            documentImage.style.display = "block";
            documentImage.classList.remove("hidden");
            documentImage.style.width = "100%";
            documentImage.style.height = "auto";
            documentImage.style.maxHeight = "200px";
            documentImage.style.objectFit = "contain";
            
            // Hide the placeholder icon
            documentImageIcon.style.display = "none";
            documentImageIcon.classList.add("hidden");
            
            // Mark file as uploaded
            if (fileUploadedField) {
                fileUploadedField.value = 'true';
            }
            
        } catch (error) {
            // Failed to restore preview - clean up storage
            localStorage.removeItem(`docFile-${formIndex}`);
        }
    } else if (alreadyTracked && !hasServerPreview) {
        // File was tracked but preview missing - mark as uploaded anyway
        if (fileUploadedField) {
            fileUploadedField.value = 'true';
        }
    } else if (hasServerPreview) {
        // Server already provided preview - mark as uploaded
        if (fileUploadedField) {
            fileUploadedField.value = 'true';
        }
    }
}

function handleDocumentPreview(e, formIndex) {
    const file = e.target.files[0];
    if (!file) {
        // File was cleared - but DON'T clear tracking if it was previously uploaded
        const fileUploadedField = document.getElementById(`file-uploaded-${formIndex}`);
        const hadPreviousFile = localStorage.getItem(`docFile-${formIndex}`) || 
                               sessionStorage.getItem(`doc-${formIndex}-had-file`) === 'true';
        
        if (fileUploadedField && !hadPreviousFile) {
            fileUploadedField.value = 'false';
        }
        return;
    }
    
    // Find the correct image and icon elements for this form
    const documentImage = document.getElementById(`document-image-${formIndex}`);
    const documentImageIcon = document.getElementById(`document-image-icon-${formIndex}`);
    
    if (!documentImage || !documentImageIcon) {
        return;
    }
    
    // AGGRESSIVELY mark as uploaded in multiple places
    const fileUploadedField = document.getElementById(`file-uploaded-${formIndex}`);
    if (fileUploadedField) {
        fileUploadedField.value = 'true';
    }
    
    // Mark in sessionStorage for future validation cycles
    sessionStorage.setItem(`doc-${formIndex}-had-file`, 'true');
    
    // Add data attribute to the input itself
    e.target.setAttribute('data-has-file', 'true');
    
    // Check file type and show appropriate preview
    const fileType = file.type;
    const fileName = file.name.toLowerCase();
    
    if (fileType.startsWith('image/') || fileName.match(/\.(jpg|jpeg|png|gif|bmp)$/)) {
        // Handle image files
        const url = window.URL.createObjectURL(file);
        
        // Show the image preview
        documentImage.src = url;
        documentImage.style.display = "block";
        documentImage.classList.remove("hidden");
        documentImage.style.width = "100%";
        documentImage.style.height = "auto";
        documentImage.style.maxHeight = "200px";
        documentImage.style.objectFit = "contain";
        
    } else if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
        // Handle PDF files - show a PDF icon
        documentImage.src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZT0iY3VycmVudENvbG9yIiBjbGFzcz0idy02IGgtNiI+CiAgPHBhdGggc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBkPSJNMTkuNSAxNEE3LjUgNy41IDAgMSAxIDEyIDYuNWgzLjE4NEExLjUgMS41IDAgMCAxIDE2LjY3IDcuODA3bDMuMzU3IDUuMDM2YTEuNSAxLjUgMCAwIDEtLjUyNyAyLjE1N1oiIC8+Cjwvc3ZnPgo=";
        documentImage.style.display = "block";
        documentImage.classList.remove("hidden");
        documentImage.style.width = "60px";
        documentImage.style.height = "60px";
        
        // Create a label to show it's a PDF
        let pdfLabel = documentImage.parentNode.querySelector('.pdf-label');
        if (!pdfLabel) {
            pdfLabel = document.createElement('div');
            pdfLabel.className = 'pdf-label';
            pdfLabel.style.cssText = 'position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.7); color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;';
            documentImage.parentNode.appendChild(pdfLabel);
        }
        pdfLabel.textContent = 'PDF';
        
    } else {
        // Handle other file types - show a generic document icon
        documentImage.src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZT0iY3VycmVudENvbG9yIj4KICA8cGF0aCBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGQ9Im05IDEyaDMuNzVtLTkuNzUgMGgzLjc1bTIuMjUtMyAzIDNMLjI1IDEwLjUiLz4KPC9zdmc+Cg==";
        documentImage.style.display = "block";
        documentImage.classList.remove("hidden");
        documentImage.style.width = "60px";
        documentImage.style.height = "60px";
    }
    
    // Hide the placeholder icon
    documentImageIcon.style.display = "none";
    documentImageIcon.classList.add("hidden");
    
    // Store file for restoration after validation failures
    const reader = new FileReader();
    reader.onload = function(e) {
        const base64 = e.target.result;
        localStorage.setItem(`docFile-${formIndex}`, base64);
        // Also store a timestamp to track how recent this is
        localStorage.setItem(`docFile-${formIndex}-timestamp`, Date.now().toString());
    };
    reader.readAsDataURL(file);
}

//----------add new document form-----------------//

function setupAddDocumentButton() {
    // Document formset management
    const documentFormset = document.getElementById('document-formset');
    const newDocForm = document.querySelector('.new-doc-form');

    if (!addDocumentBtn || !documentFormset) {
        return; // Exit if required elements are not found
    }

    // Check if already bound to prevent duplicate listeners
    if (addDocumentBtn.hasAttribute('data-listener-bound')) {
        return;
    }

    // Store the original template form
    let documentTemplate = null;
    if (documentFormset) {
        const existingForm = document.querySelector('.document-form');
        if (existingForm) {
            documentTemplate = existingForm.cloneNode(true);
        }
    }
    
    let formIdx = parseInt(document.querySelector('#id_documents-TOTAL_FORMS').value);
    
    // Mark button as bound to prevent duplicate listeners
    addDocumentBtn.setAttribute('data-listener-bound', 'true');
    
    addDocumentBtn.addEventListener('click', function(e) {
        e.preventDefault(); // Prevent any default button behavior

      
        let emptyForm;
        
        // check if doc form 

        // Check if we have existing forms to clone from
        const existingForm = document.querySelector('.document-form');
        if (existingForm) {
            emptyForm = existingForm.cloneNode(true);
        } else if (documentTemplate) {
            // Use stored template if no existing forms
            emptyForm = documentTemplate.cloneNode(true);
        } else {
            // Create new form from scratch if no template exists
            emptyForm = createNewDocumentForm(formIdx);
        }
        
        // Ensure we have a form to work with
        if (!emptyForm) {
            alert('Error: Could not create new document form. Please refresh the page and try again.');
            return;
        }
        
        emptyForm.dataset.formIdx = formIdx;
        
        // Update form indexes
        const formIdxRegex = new RegExp('documents-\\d+-', 'g');
        emptyForm.innerHTML = emptyForm.innerHTML.replace(formIdxRegex, 'documents-' + formIdx + '-');
        
        // Clear values and reset form state - PRESERVE FORMSET MANAGEMENT FIELDS
        emptyForm.querySelectorAll('input, select, textarea').forEach(function(input) {
            // CRITICAL: Never modify Django formset management fields
            if (input.name && (
                input.name.includes('-id') || 
                input.name.includes('-DELETE') ||
                input.name.includes('TOTAL_FORMS') ||
                input.name.includes('INITIAL_FORMS')
            )) {
                // For new forms, clear the id field but keep the field itself
                if (input.name.includes('-id')) {
                    input.value = '';
                }
                return; // Skip further processing for management fields
            }
            
            if (input.type !== 'hidden') {
                input.value = '';
            }
            
            // Update file input ID
            if(input.type == "file"){
                input.setAttribute("id", `id_documents-${formIdx}-document_file`);
            }
            
            // Reset upload tracking hidden field for new documents
            if(input.name && input.name.includes('-file_uploaded')){
                input.value = 'false';
                input.setAttribute("id", `file-uploaded-${formIdx}`);
            }

            // if(input.tagName === 'SELECT'){
            //     for (let i = 0; i < input.options.length; i++) {
            //         if (input.options[i].value === "passport") {
            //             input.remove(i);
            //             break;
            //         }
                    
            //     }
                
            // }

            
            
           
        });
        
        // Update image preview element IDs
        emptyForm.querySelector('.document-image-icon').setAttribute("id",`document-image-icon-${formIdx}`);
        emptyForm.querySelector('.document-image').setAttribute("id",`document-image-${formIdx}`);

        // Reset preview state for new form
        emptyForm.querySelectorAll('.document-image').forEach(function(img){
            img.style.display = "none";
            img.classList.add("hidden");
            img.src = "";
            // Remove any error handlers from cloned images
            img.removeAttribute('onerror');
        });

        emptyForm.querySelectorAll('.document-image-icon').forEach(function(icon){
            icon.style.display = "flex";
            icon.classList.remove("hidden");
            
            // Ensure proper placeholder content for new forms
            const iconElement = icon.querySelector('i');
            const textElement = icon.querySelector('span');
            if (iconElement) {
                iconElement.className = "bi bi-image text-gray-500";
                iconElement.style.fontSize = "46px";
            }
            if (textElement) {
                textElement.textContent = "No document uploaded";
                textElement.className = "text-xs text-gray-500 text-center";
            }
        })
  
        // Update form title and numbering
        emptyForm.querySelector('h5').textContent = 'Document #' + (formIdx + 1);
        
        // Show remove button for new forms (hide delete checkbox)
        const deleteCheckbox = emptyForm.querySelector('.delete-checkbox');
        const removeBtn = emptyForm.querySelector('.btn-doc-close');
        if (deleteCheckbox) {
            deleteCheckbox.style.display = 'none';
        }
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
        }
        
        const requiredDoc = emptyForm.querySelectorAll('[required]');

        requiredDoc.forEach(function(input){
            input.style.borderColor = ''; 
            input.style.boxShadow = '';  
        })

        // Remove only error message spans, not all spans (preserve formset structure)
        const errorSpans = emptyForm.querySelectorAll('span.text-danger, span.text-red-500, span.error');
        errorSpans.forEach(function(span){
            span.remove();
        })
        
        // Remove any server-provided file existence indicators
        const fileExistsIndicators = emptyForm.querySelectorAll('.text-success, .doc-img-preview');
        fileExistsIndicators.forEach(function(indicator){
            indicator.remove();
        })

        // Insert the new form into the document formset
        if (newDocForm && newDocForm.parentNode) {
            newDocForm.parentNode.insertBefore(emptyForm, newDocForm);
        } else {
            // Fallback: insert before the add button
            addDocumentBtn.parentNode.insertBefore(emptyForm, addDocumentBtn);
        }
        
        // Update total forms count
        formIdx++;
        document.querySelector('#id_documents-TOTAL_FORMS').value = formIdx;

        //remove text error for document
        let errorText = emptyForm.querySelectorAll('span');
        errorText.forEach(span=>{
            if(span.getAttribute("id")){
                span.remove();
            }
                
        })

        //remove text error for document
        let fileUploadRequired = emptyForm.querySelectorAll(`input[type="file"][name*="document_file"]`);
        fileUploadRequired.forEach(fileUpld=>{
            fileUpld.setAttribute("required", "")            
        })
        // Update document numbers for all forms
        updateDocumentNumbers();
        
        // Initialize inline validation for the new form
        if (typeof initializeInlineValidation === 'function') {
            const newFormFields = emptyForm.querySelectorAll('input, select, textarea');
            newFormFields.forEach(field => {
                // Skip Django formset management fields
                if (field.type === 'hidden' || 
                    field.name.includes('-id') || 
                    field.name.includes('-DELETE') || 
                    field.name.includes('TOTAL_FORMS') || 
                    field.name.includes('INITIAL_FORMS')) {
                    return; // Skip adding listeners to these fields
                }
                
                // Only add validation listeners to user-input fields, not formset management fields
                if (!field.name || (!field.name.includes('-id') && !field.name.includes('-DELETE'))) {
                field.addEventListener('blur', (e) => {
                    if (typeof validateDocumentField === 'function') {
                        validateDocumentField(e.target, formIdx - 1);
                    }
                });
                field.addEventListener('input', (e) => {
                    if (typeof hasError === 'function' && typeof clearErrorStyle === 'function') {
                        if (hasError(e.target)) {
                            clearErrorStyle(e.target);
                        }
                    }
                });
                field.addEventListener('change', (e) => {
                    if (typeof validateDocumentField === 'function') {
                        validateDocumentField(e.target, formIdx - 1);
                    }
                });
                }
            });
        }
        
        // Initialize document preview for the new form
        const newFileInput = emptyForm.querySelector(`input[type="file"][name*="document_file"]`);
        const newDocTypeSelect = emptyForm.querySelector(`select[name*="document_type"]`);
        
        if (newFileInput) {
            newFileInput.addEventListener('change', function(e) {
                handleDocumentPreview(e, formIdx - 1);
                checkDocumentTypeReplacement();
            });
        }
        
        if (newDocTypeSelect) {
            newDocTypeSelect.addEventListener('change', function(e) {
                checkDocumentTypeReplacement();
            });
        }
        
        // Check for conflicts after adding new form
        setTimeout(() => checkDocumentTypeReplacement(), 100);
    });
    
}
// Function to remove a document form
function removeDocumentForm(button) {
    const documentForm = button.closest('.document-form');
    if (documentForm) {
        // Get the form index before removing
        const formIndex = Array.from(document.querySelectorAll('.document-form')).indexOf(documentForm);
        
        // Clean up localStorage for this form
        localStorage.removeItem(`docFile-${formIndex}`);
        
        documentForm.remove();
        
        // Update total forms count
        const totalForms = document.querySelector('#id_documents-TOTAL_FORMS');
        totalForms.value = parseInt(totalForms.value) - 1;
        
        // Update document numbers for remaining forms
        updateDocumentNumbers();
        
        // Check for document type conflicts after removal
        setTimeout(() => checkDocumentTypeReplacement(), 100);
        
        // Clean up localStorage for all forms (since indices changed)
        cleanupStorageAfterReorder();

    }
}

// Clean up localStorage when forms are reordered
function cleanupStorageAfterReorder() {
    // Get all current forms
    const documentForms = document.querySelectorAll('.document-form');
    
    // Clean up localStorage for indices beyond current form count
    for (let i = documentForms.length; i < 10; i++) { // Assuming max 10 forms
        localStorage.removeItem(`docFile-${i}`);
    }
}

// Clean up all document preview storage (call on successful form submission)
function cleanupAllDocumentStorage() {
    for (let i = 0; i < 10; i++) { // Assuming max 10 forms
        localStorage.removeItem(`docFile-${i}`);
        localStorage.removeItem(`docFile-${i}-timestamp`);
        sessionStorage.removeItem(`doc-${i}-had-file`);
    }
    // Document preview storage cleaned up
}

// Clear all visible document previews (force reset to placeholder state)
function clearAllVisiblePreviews() {
    const documentForms = document.querySelectorAll('.document-form');
    
    documentForms.forEach((form, index) => {
        const documentImage = form.querySelector('.document-image');
        const documentImageIcon = form.querySelector('.document-image-icon');
        const fileUploadedField = form.querySelector(`input[name*="-file_uploaded"]`);
        
        if (documentImage) {
            documentImage.src = '';
            documentImage.style.display = 'none';
            documentImage.classList.add('hidden');
        }
        
        if (documentImageIcon) {
            documentImageIcon.style.display = 'flex';
            documentImageIcon.classList.remove('hidden');
            
            // Ensure proper placeholder content
            const iconElement = documentImageIcon.querySelector('i');
            const textElement = documentImageIcon.querySelector('span');
            if (iconElement && !iconElement.classList.contains('text-gray-500')) {
                iconElement.className = "bi bi-image text-gray-500";
                iconElement.style.fontSize = "46px";
            }
            if (textElement && textElement.textContent !== "No document uploaded") {
                textElement.textContent = "No document uploaded";
                textElement.className = "text-xs text-gray-500 text-center";
            }
        }
        
        if (fileUploadedField) {
            fileUploadedField.value = 'false';
        }
        
        // Clear any file inputs
        const fileInput = form.querySelector(`input[type="file"]`);
        if (fileInput) {
            fileInput.value = '';
            fileInput.removeAttribute('data-has-file');
        }
    });
}

// Function to update document numbers
function updateDocumentNumbers() {
    const documentForms = document.querySelectorAll('.document-form');   

    documentForms.forEach((form, index) => {

        const title = form.querySelector('h5');
        
        if (title) {
            title.textContent = 'Document #' + (index + 1);
        }
        
        // Update the IDs of image and icon elements to match new numbering
        const documentImage = form.querySelector('.document-image');
        const documentImageIcon = form.querySelector('.document-image-icon');
        
        if (documentImage) {
            documentImage.id = `document-image-${index}`;
        }
        if (documentImageIcon) {
            documentImageIcon.id = `document-image-icon-${index}`;
        }
        
        // Re-initialize file input event listener with correct index
        const fileInput = form.querySelector(`input[type="file"][name*="document_file"]`);
        if (fileInput) {
            // Remove existing listeners to prevent duplicates
            const newFileInput = fileInput.cloneNode(true);
            fileInput.parentNode.replaceChild(newFileInput, fileInput);
            
            // Add new listener with correct index
            newFileInput.addEventListener('change', function(e) {
                handleDocumentPreview(e, index);
            });
        }

         // check doc type limit
         if(index == 4){
            addDocumentBtn.setAttribute("disabled", "disabled")
         }else{
            addDocumentBtn.removeAttribute("disabled")
         }

       


    });
}



function createNewDocumentForm(formIdx) {
    const formHtml = `
        <div class="document-form border mx-3 rounded my-3" data-form-idx="${formIdx}">
            <div class="flex justify-between items-center px-3 bg-gray-100 py-2 border-b">
                <h5 class="font-medium text-blue-500 flex items-center space-x-2 mb-0 pb-0">Document #${formIdx + 1}</h5>
                <div class="d-flex align-items-center">
                    <button type="button" class="btn-doc-close btn btn-sm btn-outline-danger me-2" onclick="removeDocumentForm(this)">
                        <i class="bi bi-x-lg"></i>
                        <span class="d-none d-md-inline ms-1">Remove</span>
                    </button>
                </div>
            </div>
            
            <!-- Hidden formset management fields for Django -->
            <input type="hidden" name="documents-${formIdx}-id" id="id_documents-${formIdx}-id" value="">
            <input type="hidden" name="documents-${formIdx}-DELETE" id="id_documents-${formIdx}-DELETE" value="false">
            
            <div class="grid grid-cols-3 gap-4 px-3 py-1 mb-2 mt-3">
                <div class="border rounded col-span-1">
                    <div class="border-b border-gray-200 px-3 py-2">
                        <h4 class="text-[16px] font-semibold"><i class="bi bi-image me-2"></i>Document Review</h4>
                    </div>
                    <div class="px-3 py-3 space-y-3">
                        <div class="relative image-preview-card px-2 py-3 border rounded bg-gray-100 flex flex-col items-center justify-center" style="border:2px dotted #999 !important; min-height:200px; position:relative;">
                            <div id="document-image-icon-${formIdx}" class="document-image-icon flex flex-col items-center justify-center">
                                <i class="bi bi-image text-gray-500" style="font-size:46px;"></i>
                                <span class="text-xs text-gray-500 text-center">No document uploaded</span>
                            </div>
                            <img src="" alt="document" id="document-image-${formIdx}" class="document-image rounded hidden">
                        </div>
                        <div class="flex flex-col gap-2">
                            <label for="id_documents-${formIdx}-document_file" class="text-sm font-medium">
                                <i class="bi bi-cloud-upload me-2"></i> Upload File
                            </label>
                            <div class="rounded" style="border:2px dotted #999 !important;">
                                <input type="file" name="documents-${formIdx}-document_file" class="form-control" id="id_documents-${formIdx}-document_file">
                                <!-- Hidden field to track if file was uploaded -->
                                <input type="hidden" id="file-uploaded-${formIdx}" name="documents-${formIdx}-file_uploaded" value="false">
                            </div>
                            <small class="flex justify-center w-full text-muted text-center mt-2">Supported: JPG, PNG, PDF (Max 5MB)</small>
                        </div>
                    </div>
                </div>
                
                <div class="border rounded col-span-2">
                    <div class="border-b border-gray-200 px-3 py-2">
                        <h4 class="text-[16px] font-semibold"><i class="bi bi-info-circle me-2"></i>Document Info</h4>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 px-3 py-2">
                        <div class="flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-document_type" class="text-xs font-medium">Document Type<span class="text-red-500">*</span></label>
                            <select name="documents-${formIdx}-document_type" class="form-select" id="id_documents-${formIdx}-document_type">
                                <option value="">---------</option>
                                <option value="passport">Passport</option>
                                <option value="id_card">ID Card</option>
                                <option value="driving_license">Driving License</option>
                                <option value="work_permit">Work Permit</option>
                                <option value="visa">Visa</option>
                                <option value="certificate">Certificate</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div class="flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-document_number" class="text-xs font-medium">Document Number<span class="text-red-500">*</span></label>
                            <input type="text" name="documents-${formIdx}-document_number" class="form-control" id="id_documents-${formIdx}-document_number">
                        </div>
                        <div class="flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-issue_date" class="text-xs font-medium">Issue Date<span class="text-red-500">*</span></label>
                            <input type="date" name="documents-${formIdx}-issue_date" class="form-control" id="id_documents-${formIdx}-issue_date">
                        </div>
                        <div class="flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-expiry_date" class="text-xs font-medium">Expiry Date<span class="text-red-500">*</span></label>
                            <input type="date" name="documents-${formIdx}-expiry_date" class="form-control" id="id_documents-${formIdx}-expiry_date">
                        </div>
                        <div class="col-span-2 flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-issuing_authority" class="text-xs font-medium">Issuing Authority<span class="text-red-500">*</span></label>
                            <input type="text" name="documents-${formIdx}-issuing_authority" class="form-control" id="id_documents-${formIdx}-issuing_authority">
                        </div>
                        <div class="col-span-2 flex flex-col gap-1">
                            <label for="id_documents-${formIdx}-notes" class="text-xs font-medium">Note</label>
                            <textarea name="documents-${formIdx}-notes" class="form-control" id="id_documents-${formIdx}-notes" rows="2"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = formHtml;
    return tempDiv.firstElementChild;
}

/**
 * Check for document type conflicts and warn users about automatic replacement
 */
function checkDocumentTypeReplacement() {
    const autoReplaceTypes = ['passport', 'id_card', 'visa', 'work_permit'];
    const documentForms = document.querySelectorAll('.document-form');
    const typeCount = {};
    const warnings = {};
    
    // Clear existing warnings
    document.querySelectorAll('.document-replacement-warning').forEach(warning => {
        warning.remove();
    });
    
    // Count document types and identify conflicts
    documentForms.forEach((form, index) => {
        const docTypeSelect = form.querySelector(`select[name*="document_type"]`);
        const fileInput = form.querySelector(`input[type="file"][name*="document_file"]`);
        const deleteCheckbox = form.querySelector(`input[name*="DELETE"]`);
        
        if (!docTypeSelect || !docTypeSelect.value) return;
        if (deleteCheckbox && deleteCheckbox.checked) return; // Skip documents marked for deletion
        
        const docType = docTypeSelect.value;
        
        if (autoReplaceTypes.includes(docType)) {
            if (!typeCount[docType]) {
                typeCount[docType] = [];
            }
            typeCount[docType].push({
                form: form,
                index: index,
                hasFile: fileInput && fileInput.files.length > 0,
                hasExistingFile: form.querySelector('.doc-img-preview') !== null,
                select: docTypeSelect
            });
        }
    });
    
    // Show warnings for conflicts
    Object.keys(typeCount).forEach(docType => {
        const instances = typeCount[docType];
        if (instances.length > 1) {
            const docTypeName = getDocumentTypeName(docType);
            
            instances.forEach((instance, idx) => {
                if (idx > 0 || instances.some(inst => inst.hasFile)) {
                    showReplacementWarning(instance.form, docTypeName, instances.length);
                }
            });
        }
    });
}

/**
 * Get human-readable document type name
 */
function getDocumentTypeName(docType) {
    const typeNames = {
        'passport': 'Passport',
        'visa': 'Visa', 
        'work_permit': 'Work Permit'
    };
    return typeNames[docType] || docType;
}

/**
 * Show replacement warning for a document form
 */
function showReplacementWarning(form, docTypeName, count) {
    // Remove existing warning if any
    const existingWarning = form.querySelector('.document-replacement-warning');
    if (existingWarning) {
        existingWarning.remove();
    }
    
    // Create warning element
    const warningDiv = document.createElement('div');
    warningDiv.className = 'document-replacement-warning alert alert-warning mt-2 mb-2';
    warningDiv.style.padding = '8px 12px';
    warningDiv.style.fontSize = '12px';
    warningDiv.style.backgroundColor = '#fef3cd';
    warningDiv.style.borderColor = '#faebcc';
    warningDiv.style.color = '#856404';
    warningDiv.style.borderRadius = '4px';
    warningDiv.style.border = '1px solid';
    
    warningDiv.innerHTML = `
        <i class="fa fa-exclamation-triangle me-1"></i>
        <strong>Document Replacement:</strong> Multiple ${docTypeName} documents detected. 
        The previous ${docTypeName} will be automatically replaced when you save.
    `;
    
    // Insert warning after the document type selector
    const docTypeDiv = form.querySelector(`select[name*="document_type"]`);
    if (docTypeDiv) {
        docTypeDiv.parentNode.insertBefore(warningDiv, docTypeDiv.nextSibling);
    }
}

/**
 * Delete an existing document with confirmation modal
 */
function deleteDocument(button, documentId, documentType) {
    // Store reference for modal confirmation
    window.pendingDeletion = {
        button: button,
        documentId: documentId,
        documentType: documentType
    };
    
    // Update modal message with document type
    const messageElement = document.getElementById('deleteConfirmMessage');
    if (messageElement) {
        messageElement.textContent = `Are you sure you want to delete this ${documentType} document? This action cannot be undone and the document file will be permanently removed.`;
    }
    
    // Show the modal
    showDeleteModal();
}

/**
 * Show delete confirmation modal
 */
function showDeleteModal() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Attach event listener to confirm button
        const confirmBtn = document.getElementById('docConfirmDeleteBtn');
        if (confirmBtn) {
            confirmBtn.onclick = function() {
                confirmDeleteDocument();
            };
        }
    }
}

/**
 * Close delete confirmation modal
 */
function closeDeleteModal() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Clear pending deletion
        window.pendingDeletion = null;
    }
}

/**
 * Confirm and execute document deletion
 */
function confirmDeleteDocument() {
    if (!window.pendingDeletion) {
        return;
    }
    
    const { button, documentId, documentType } = window.pendingDeletion;
    
    // Find the document form container
    const documentForm = button.closest('.document-form');
    if (!documentForm) {
        closeDeleteModal();
        return;
    }
    
    // Find and check the DELETE checkbox
    const deleteCheckbox = documentForm.querySelector('input[name*="DELETE"]');
    if (deleteCheckbox) {
        deleteCheckbox.checked = true;
        
        // Add visual indication that document is marked for deletion
        documentForm.classList.add('ring-2', 'ring-red-200', 'bg-red-50','opacity-50', 'border-danger');
        // documentForm.style.opacity = '0.5';
        // documentForm.style.background = '#fff5f5';
    
        
        // Update the document header to show deletion status
        const headerTitle = documentForm.querySelector('h5');
        if (headerTitle) {
            const originalText = headerTitle.textContent;
            headerTitle.innerHTML = `<span class="text-danger"><i class="bi bi-trash me-1"></i>MARKED FOR DELETION</span> - ${originalText}`;
        }
        
        // Replace delete button with undo button
        button.innerHTML = '<div><i class="bi bi-arrow-counterclockwise"></i><span class="d-none d-md-inline ms-1">Undo</span></div>';
        button.className = 'button-min-warn me-2 opacity-100';
        button.title = 'Undo deletion';
        button.onclick = function() { undoDeleteDocument(this, documentId, documentType, headerTitle ? headerTitle.textContent : 'Document'); };
        
        // Show a toast message if available
        if (typeof toast !== 'undefined') {
            toast.warning(`${documentType} document marked for deletion. Save the form to permanently delete it.`);
        }
        
        // Check for document type conflicts after marking for deletion
        setTimeout(() => checkDocumentTypeReplacement(), 100);
    }
    
    // Close the modal
    closeDeleteModal();
}

/**
 * Undo document deletion
 */
function undoDeleteDocument(button, documentId, documentType, originalHeaderText) {
    // Find the document form container
    const documentForm = button.closest('.document-form');
    if (!documentForm) {
        return;
    }
    
    // Find and uncheck the DELETE checkbox
    const deleteCheckbox = documentForm.querySelector('input[name*="DELETE"]');
    if (deleteCheckbox) {
        deleteCheckbox.checked = false;
        
        // Remove visual indication of deletion
        documentForm.classList.remove('ring-2', 'ring-red-200', 'bg-red-50','opacity-50', 'border-danger');
        // documentForm.style.opacity = '1';
        // documentForm.style.background = '';
        // documentForm.style.border = '';
        
        // Restore the document header
        const headerTitle = documentForm.querySelector('h5');
        if (headerTitle) {
            headerTitle.textContent = originalHeaderText.replace("MARKED FOR DELETION -","");
        }
        
        // Replace undo button with delete button
        button.innerHTML = '<div><i class="bi bi-trash"></i><span class="d-none d-md-inline ms-1">Delete</span></div>';
        button.className = 'button-min-danger me-2 opacity-100';
        button.title = 'Delete this document';
        button.onclick = function() { deleteDocument(this, documentId, documentType); };
        
        // Show a toast message if available
        if (typeof toast !== 'undefined') {
            toast.info(`${documentType} document deletion cancelled.`);
        }
        
        // Check for document type conflicts after undoing deletion
        setTimeout(() => checkDocumentTypeReplacement(), 100);
        
    }
}
