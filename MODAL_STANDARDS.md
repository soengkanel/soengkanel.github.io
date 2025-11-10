# Modal Standards Documentation

**⚠️ IMPORTANT:** This document has been superseded by more comprehensive guides:
- **For implementation:** See `docs/MODAL_IMPLEMENTATION_GUIDE.md`
- **For quick reference:** See `docs/MODAL_QUICK_REFERENCE.md`
- **For checklists:** See `docs/MODAL_CHECKLIST_TEMPLATE.md`

This document explains how to use the standardized modal system in the NextHR application.

## Overview

The standard modal system provides:
- ✅ Fixed center positioning (no auto-scroll)
- ✅ Proper z-index hierarchy
- ✅ Clickable interactive elements
- ✅ Smooth animations
- ✅ Responsive design
- ✅ Automatic backdrop management

## Quick Start

### 1. Include the CSS and JS files

Add these to your base template (e.g., `base/base.html`):

```html
<!-- In <head> section, after Bootstrap CSS -->
<link rel="stylesheet" href="{% static 'css/standard-modal.css' %}">

<!-- Before </body>, after Bootstrap JS -->
<script src="{% static 'js/standard-modal.js' %}"></script>
```

### 2. Create a Modal

Use standard Bootstrap modal markup with appropriate classes:

```html
<!-- Basic Modal -->
<div class="modal fade modal-level-2" id="myModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-info-circle me-1"></i>
                    My Modal Title
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Modal content goes here...</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="button-min-warn py-1" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>
                    Cancel
                </button>
                <button type="button" class="button-min-primary py-1" id="confirmBtn">
                    <i class="bi bi-check-circle me-1"></i>
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
```

### 3. Initialize the Modal (Optional)

If using custom JavaScript initialization:

```javascript
// The standard-modal.js auto-initializes all modals
// But you can also manually initialize:
const myModal = new bootstrap.Modal(document.getElementById('myModal'));
myModal.show();
```

## Modal Levels

Use the appropriate level class based on the modal's purpose:

### Level 1 - Base Modals
```html
<div class="modal fade modal-level-1" id="baseModal">
```
- **Z-Index:** 1060
- **Backdrop Z-Index:** 1055
- **Use for:** Basic information modals

### Level 2 - View/Edit Modals (Default)
```html
<div class="modal fade modal-level-2" id="viewModal">
```
- **Z-Index:** 1070
- **Backdrop Z-Index:** 1065
- **Use for:** View details, Edit forms

### Level 3 - Action Modals
```html
<div class="modal fade modal-level-3" id="approveModal">
```
- **Z-Index:** 1080
- **Backdrop Z-Index:** 1075
- **Use for:** Approve, Reject, Confirm actions

### Level 4 - Critical Modals
```html
<div class="modal fade modal-level-4" id="deleteModal">
```
- **Z-Index:** 1090
- **Backdrop Z-Index:** 1085
- **Use for:** Delete, Critical warnings

## Modal Sizes

### Small Modal
```html
<div class="modal fade modal-level-2" id="smallModal">
    <div class="modal-dialog modal-sm">
```
- Width: 400px (Desktop)

### Default Modal
```html
<div class="modal fade modal-level-2" id="defaultModal">
    <div class="modal-dialog">
```
- Width: 500px (Desktop)

### Large Modal
```html
<div class="modal fade modal-level-2" id="largeModal">
    <div class="modal-dialog modal-lg">
```
- Width: 800px (Desktop)

### Extra Large Modal
```html
<div class="modal fade modal-level-2" id="xlModal">
    <div class="modal-dialog modal-xl">
```
- Width: 1140px (Desktop)

## Form Controls in Modals

The standard CSS automatically styles form elements:

```html
<div class="modal-body">
    <div class="mb-2">
        <label for="inputField" class="form-label">Field Label</label>
        <input type="text" id="inputField" class="form-control" placeholder="Enter value...">
    </div>

    <div class="mb-2">
        <label for="selectField" class="form-label">Select Field</label>
        <select id="selectField" class="form-select">
            <option value="">Choose...</option>
            <option value="1">Option 1</option>
        </select>
    </div>

    <div class="mb-2">
        <label for="textareaField" class="form-label">Textarea</label>
        <textarea id="textareaField" class="form-control" rows="3"></textarea>
    </div>
</div>
```

## Best Practices

### 1. Always Use Icons
```html
<h5 class="modal-title">
    <i class="bi bi-exclamation-triangle-fill text-danger me-1"></i>
    Delete Confirmation
</h5>
```

### 2. Consistent Button Styling
```html
<div class="modal-footer">
    <div class="d-flex gap-1 w-100 justify-content-end">
        <button type="button" class="button-min-warn py-1" data-bs-dismiss="modal">
            <i class="bi bi-x-circle me-1"></i>
            Cancel
        </button>
        <button type="button" class="button-min-danger py-1" id="deleteBtn">
            <i class="bi bi-trash3 me-1"></i>
            Delete
        </button>
    </div>
</div>
```

### 3. Loading States
```javascript
const confirmBtn = document.getElementById('confirmBtn');
const originalContent = confirmBtn.innerHTML;

// Show loading
confirmBtn.disabled = true;
confirmBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Processing...';

// Restore after action
confirmBtn.disabled = false;
confirmBtn.innerHTML = originalContent;
```

### 4. CSRF Token Handling
```javascript
function getCSRFToken() {
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) return csrfMeta.getAttribute('content');

    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) return csrfInput.value;

    const csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrfCookie) return csrfCookie[1];

    return null;
}
```

## Examples

### Delete Confirmation Modal

```html
<div class="modal fade modal-level-4" id="deleteModal" tabindex="-1">
    <div class="modal-dialog modal-sm">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-exclamation-triangle-fill text-danger me-1"></i>
                    <span id="deleteModalTitle">Delete Item?</span>
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p id="deleteModalName" class="mb-2" style="font-size: 12px; font-weight: 500;"></p>
                <p class="text-muted mb-0" style="font-size: 11px;">
                    <i class="bi bi-info-circle me-1"></i>
                    This action cannot be undone
                </p>
            </div>
            <div class="modal-footer">
                <div class="d-flex gap-1 w-100 justify-content-end">
                    <button type="button" class="button-min-warn py-1" data-bs-dismiss="modal">
                        <i class="bi bi-x-circle me-1"></i>
                        Cancel
                    </button>
                    <button type="button" class="button-min-danger py-1" id="confirmDeleteBtn">
                        <i class="bi bi-trash3 me-1"></i>
                        Delete
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```

### View Details Modal

```html
<div class="modal fade modal-level-2" id="viewModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-eye me-1"></i>
                    View Details
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Details content -->
                <div class="row g-3">
                    <div class="col-6">
                        <label class="form-label">Field 1</label>
                        <p id="field1" style="font-size: 12px; font-weight: 600;"></p>
                    </div>
                    <div class="col-6">
                        <label class="form-label">Field 2</label>
                        <p id="field2" style="font-size: 12px; font-weight: 600;"></p>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="button-min-default py-1" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>
                    Close
                </button>
            </div>
        </div>
    </div>
</div>
```

## Troubleshooting

### Modal backdrop blocks interaction
**Solution:** Make sure you've included `standard-modal.js` and the modal has a level class.

### Modal scrolls page when opening
**Solution:** The standard CSS should handle this automatically. Verify `standard-modal.css` is loaded.

### Buttons not clickable
**Solution:** Ensure `pointer-events: auto !important` is applied (automatic with standard-modal.css).

### Wrong z-index stacking
**Solution:** Use the appropriate modal level class (modal-level-1 through modal-level-4).

## Migration Guide

To migrate existing modals to the standard system:

1. **Add the CSS and JS files** to your base template
2. **Add a level class** to your modal:
   ```html
   <div class="modal fade modal-level-2" id="yourModal">
   ```
3. **Remove custom z-index styles** - let the standard system handle it
4. **Remove custom positioning JavaScript** - it's now automatic
5. **Test all interactions** - close buttons, ESC key, backdrop click

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Changelog

### Version 1.0.0 (2025-01-06)
- Initial release
- Fixed center positioning
- Automatic backdrop management
- Z-index hierarchy system
- Responsive design
- Mobile optimizations
