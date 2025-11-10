# Modal Quick Reference Card

**Print this and keep it at your desk!**

---

## 🚀 Quick Start (Copy & Paste)

```html
<div class="modal fade modal-level-2" id="myModal" tabindex="-1"
     aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="myModalLabel">
                    <i class="bi bi-icon me-1"></i>Title
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">Content here</div>
            <div class="modal-footer">
                <div class="d-flex gap-1 w-100 justify-content-end">
                    <button class="button-min-warn py-1" data-bs-dismiss="modal">
                        <i class="bi bi-x-circle me-1"></i>Cancel
                    </button>
                    <button class="button-min-primary py-1" id="confirmBtn">
                        <i class="bi bi-check-circle me-1"></i>Confirm
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## 📊 Modal Levels (Choose ONE)

| Class | Z-Index | Use For |
|-------|---------|---------|
| `modal-level-1` | 1060 | Info/Help |
| `modal-level-2` | 1070 | **View/Edit (DEFAULT)** |
| `modal-level-3` | 1080 | Approve/Reject |
| `modal-level-4` | 1090 | **Delete/Critical** |

---

## 📐 Modal Sizes

```html
<div class="modal-dialog modal-sm">     <!-- 400px -->
<div class="modal-dialog">              <!-- 500px DEFAULT -->
<div class="modal-dialog modal-lg">     <!-- 800px -->
<div class="modal-dialog modal-xl">     <!-- 1140px -->
```

---

## ✅ Must-Have Attributes

```html
class="modal fade modal-level-X"  ✅ Required
id="uniqueId"                     ✅ Required
tabindex="-1"                     ✅ Required
aria-labelledby="uniqueIdLabel"   ✅ Required
aria-hidden="true"                ✅ Required
```

---

## 🎨 Button Colors

```html
<!-- Primary (Blue) -->
<button class="button-min-primary py-1">

<!-- Success (Green) -->
<button class="button-min-success py-1">

<!-- Danger (Red) -->
<button class="button-min-danger py-1">

<!-- Warning (Yellow) -->
<button class="button-min-warn py-1">

<!-- Default (Gray) -->
<button class="button-min-default py-1">
```

---

## 🔧 Common Icons

```html
<i class="bi bi-info-circle"></i>           <!-- Info -->
<i class="bi bi-eye"></i>                   <!-- View -->
<i class="bi bi-pencil-square"></i>         <!-- Edit -->
<i class="bi bi-trash3"></i>                <!-- Delete -->
<i class="bi bi-check-circle"></i>          <!-- Confirm/Success -->
<i class="bi bi-x-circle"></i>              <!-- Cancel/Close -->
<i class="bi bi-exclamation-triangle"></i>  <!-- Warning -->
<i class="bi bi-hourglass-split"></i>       <!-- Loading -->
```

---

## 💻 Essential JavaScript

### Initialize Modal
```javascript
const myModal = new bootstrap.Modal(document.getElementById('myModal'));
myModal.show();
```

### Get CSRF Token
```javascript
function getCSRFToken() {
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) return csrfMeta.getAttribute('content');

    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) return csrfInput.value;

    const csrfCookie = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfCookie ? csrfCookie[1] : null;
}
```

### Loading State
```javascript
const btn = document.getElementById('confirmBtn');
const original = btn.innerHTML;

// Show loading
btn.disabled = true;
btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Processing...';

// Restore
btn.disabled = false;
btn.innerHTML = original;
```

### Reset on Close
```javascript
modalElement.addEventListener('hidden.bs.modal', function() {
    // Reset button
    confirmBtn.disabled = false;
    confirmBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Confirm';

    // Clear form
    document.getElementById('myForm').reset();
});
```

---

## ✔️ Pre-Flight Checklist

Before committing your modal:

- [ ] Uses `modal-level-X` class
- [ ] Has unique ID
- [ ] Has all required attributes
- [ ] Icons added to title and buttons
- [ ] Button colors appropriate
- [ ] Loading state implemented
- [ ] CSRF token if submitting
- [ ] Reset on close
- [ ] Tested: Open, Close, ESC, Click outside
- [ ] No console errors
- [ ] No accessibility warnings

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Modal doesn't show | Check ID, verify bootstrap loaded |
| Backdrop blocks | Already fixed - reload page |
| Not centered | Clear cache, check standard-modal.css |
| ARIA warning | Already fixed - reload page |
| Can't click buttons | Check z-index, verify modal-level class |

---

## 📚 Full Documentation

For detailed guide: `docs/MODAL_IMPLEMENTATION_GUIDE.md`
For standards: `MODAL_STANDARDS.md`

---

## 🎯 Remember

1. **Copy the template** - Don't create from scratch
2. **Choose the right level** - When in doubt, use `modal-level-2`
3. **Add icons** - They improve UX
4. **Test everything** - All 4 close methods
5. **Check console** - No errors = good to go

---

**Keep This Handy!** 📌

Print this reference and keep it visible while coding modals.
Every modal following this guide will work perfectly!

---

**Version:** 2.0 | **Updated:** January 2025
