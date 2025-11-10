# Modal Implementation Checklist

**Modal Name:** ___________________________
**Developer:** ___________________________
**Date:** ___________________________
**PR Number:** ___________________________

---

## Phase 1: Setup

- [ ] Copied modal template from guide
- [ ] Chose modal level: `modal-level-___`
- [ ] Set unique ID: `_______________`
- [ ] Set appropriate size: `modal-___` (sm/default/lg/xl)
- [ ] Added to file: `_______________`
- [ ] Verified standard-modal.css is loaded
- [ ] Verified standard-modal.js is loaded

---

## Phase 2: HTML Structure

- [ ] Modal has `class="modal fade modal-level-X"`
- [ ] Modal has unique `id` attribute
- [ ] Modal has `tabindex="-1"`
- [ ] Modal has `aria-labelledby` matching title ID
- [ ] Modal has `aria-hidden="true"`
- [ ] Close button has `data-bs-dismiss="modal"`
- [ ] Close button has `aria-label="Close"`
- [ ] Modal title has unique ID
- [ ] Modal title has icon
- [ ] All buttons have icons

---

## Phase 3: Content

- [ ] Title is clear and concise
- [ ] Body content uses proper spacing
- [ ] Form fields have labels (if applicable)
- [ ] Help text added (if needed)
- [ ] Placeholders are descriptive
- [ ] Error messages defined (if needed)
- [ ] Success messages defined (if needed)

---

## Phase 4: Buttons

- [ ] Cancel button has `button-min-warn`
- [ ] Cancel button has `data-bs-dismiss="modal"`
- [ ] Primary action button has appropriate color class
- [ ] All buttons have icons
- [ ] Button text is action-oriented
- [ ] Buttons in footer flex container
- [ ] Buttons right-aligned with `justify-content-end`

---

## Phase 5: JavaScript

- [ ] Modal initialization code added
- [ ] Button click handlers implemented
- [ ] Loading state implemented
- [ ] CSRF token obtained (if submitting)
- [ ] Error handling added
- [ ] Success handling added
- [ ] Reset on close implemented
- [ ] No console errors

---

## Phase 6: Accessibility

- [ ] Tab order is logical
- [ ] All interactive elements focusable
- [ ] ESC key closes modal (automatic)
- [ ] Focus trapped in modal when open
- [ ] Focus returns to trigger on close
- [ ] No ARIA warnings in console
- [ ] Screen reader tested (if possible)

---

## Phase 7: Testing - Functionality

- [ ] Modal opens correctly
- [ ] Modal closes with X button
- [ ] Modal closes with Cancel button
- [ ] Modal closes with ESC key
- [ ] Modal closes when clicking backdrop
- [ ] Confirm/Submit button works
- [ ] Form validation works (if applicable)
- [ ] Data saves correctly
- [ ] Error messages display correctly
- [ ] Success messages display correctly
- [ ] Modal resets on close

---

## Phase 8: Testing - Visual

- [ ] Modal appears centered on screen
- [ ] Modal doesn't cause page scroll
- [ ] Backdrop appears behind modal
- [ ] All buttons are clickable
- [ ] Loading state shows correctly
- [ ] Text is readable (size, color)
- [ ] Spacing is consistent
- [ ] Icons display correctly
- [ ] Mobile responsive (if applicable)

---

## Phase 9: Browser Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome (if applicable)
- [ ] Mobile Safari (if applicable)

---

## Phase 10: Device Testing

- [ ] Desktop 1920x1080
- [ ] Laptop 1366x768
- [ ] Tablet 768x1024 (if applicable)
- [ ] Mobile 375x667 (if applicable)

---

## Phase 11: Code Quality

- [ ] Code follows project style guide
- [ ] Console.log statements removed (or appropriate)
- [ ] Comments added where needed
- [ ] No hardcoded values (use variables)
- [ ] Error handling is comprehensive
- [ ] Code is DRY (Don't Repeat Yourself)

---

## Phase 12: Documentation

- [ ] Added comment explaining modal purpose
- [ ] Documented any special behavior
- [ ] Updated modal inventory (if applicable)
- [ ] Added to PR description
- [ ] Screenshots added (if applicable)

---

## Phase 13: Final Checks

- [ ] No console errors
- [ ] No console warnings
- [ ] No accessibility violations
- [ ] Passed all browser tests
- [ ] Passed all device tests
- [ ] Code reviewed by peer
- [ ] QA approved

---

## Issues Found (if any)

**Issue 1:**
- Description: ___________________________
- Resolution: ___________________________
- Status: [ ] Fixed [ ] Pending

**Issue 2:**
- Description: ___________________________
- Resolution: ___________________________
- Status: [ ] Fixed [ ] Pending

**Issue 3:**
- Description: ___________________________
- Resolution: ___________________________
- Status: [ ] Fixed [ ] Pending

---

## Sign-off

**Developer:** ___________________________ **Date:** ___________
- [ ] I confirm all checklist items are complete
- [ ] I have tested the modal thoroughly
- [ ] The modal follows the implementation guide

**Reviewer:** ___________________________ **Date:** ___________
- [ ] Code review passed
- [ ] Functionality verified
- [ ] Ready to merge

**QA:** ___________________________ **Date:** ___________
- [ ] QA testing passed
- [ ] No issues found
- [ ] Approved for production

---

## Notes

________________________________________________________________

________________________________________________________________

________________________________________________________________

________________________________________________________________

---

**Checklist Version:** 2.0
**Last Updated:** January 2025

**Remember:** Every checkbox matters! A thorough checklist ensures a perfect modal. 🎯
