# Employee Portal - Clean Minimal Design Guide

## Overview
A comprehensive design system for all employee portal pages featuring clean, compact, and minimal UI with white backgrounds, simple borders, and efficient layouts.

## Design System File
**Location:** `/static/css/employee-portal-clean.css`

This file contains all reusable styles for employee portal pages.

## Design Principles

✅ **Clean** - White backgrounds, simple borders
✅ **Compact** - Tight spacing, efficient layout
✅ **Minimal** - No decorative elements
✅ **Simple** - Easy to scan and use
✅ **Functional** - Focus on task completion
✅ **Fast** - Quick loading, minimal CSS

## Implementation Guide

### 1. Include CSS File

Add to the `<head>` section of your template:

```html
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/employee-portal-clean.css' %}">
{% endblock %}
```

### 2. Page Structure

```html
<div class="container-fluid px-4 py-3">
    <div class="portal-container">
        <!-- Header -->
        <div class="mb-3">
            <h5 class="page-title">Page Title</h5>
            <p class="page-subtitle">Page description</p>
        </div>

        <!-- Content goes here -->
    </div>
</div>
```

### 3. Component Usage

#### Clean Cards
```html
<div class="clean-card">
    <h6 class="section-title">Section Title</h6>
    <p>Content here</p>
</div>
```

#### Stats Cards (Grid Layout)
```html
<div class="grid-4 mb-3">
    <div class="stat-card">
        <div class="stat-number">14</div>
        <div class="stat-label">Total</div>
    </div>
    <!-- Repeat for more stats -->
</div>
```

#### Quick Actions
```html
<div class="action-grid mb-3">
    <a href="#" class="action-card">
        <div class="action-icon" style="background: #dbeafe; color: #3b82f6;">
            <i class="bi bi-calendar"></i>
        </div>
        <div class="action-label">Action</div>
    </a>
    <!-- More actions -->
</div>
```

#### Clean Tables
```html
<div class="clean-card">
    <table class="clean-table">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </tbody>
    </table>
</div>
```

#### Status Badges
```html
<span class="badge-clean badge-success">Active</span>
<span class="badge-clean badge-warning">Pending</span>
<span class="badge-clean badge-danger">Rejected</span>
<span class="badge-clean badge-info">New</span>
```

#### Buttons
```html
<button class="btn-clean-primary">Primary Action</button>
<button class="btn-clean-secondary">Secondary Action</button>
```

#### Forms
```html
<div class="mb-compact">
    <label class="form-label-clean">Field Label</label>
    <input type="text" class="form-control-clean">
</div>
```

#### Empty State
```html
<div class="empty-state">
    <i class="bi bi-inbox"></i>
    <div class="empty-state-text">No items found</div>
</div>
```

#### Info Box
```html
<div class="info-box">
    <i class="bi bi-info-circle me-1"></i>
    Important information here
</div>
```

#### List Items
```html
<div class="clean-card">
    <div class="list-item">
        <div class="list-title">Item Title</div>
        <div class="list-meta">Meta information</div>
    </div>
    <!-- More items -->
</div>
```

## Page-by-Page Implementation

### 1. Dashboard (`dashboard.html`)

**Key Changes:**
- Remove gradient header, use simple page title
- Replace fancy stats with `stat-card` grid
- Use `action-grid` for quick actions
- Simplify module cards to `clean-card`
- Use `clean-table` for recent items

**Example:**
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/employee-portal-clean.css' %}">

<div class="portal-container">
    <div class="mb-3">
        <h5 class="page-title">Dashboard</h5>
        <p class="page-subtitle">Welcome back, {{ employee.get_full_name }}</p>
    </div>

    <!-- Quick Actions -->
    <div class="action-grid mb-3">
        <a href="{% url 'leave:application_create' %}" class="action-card">
            <div class="action-icon" style="background: #fef3c7; color: #f59e0b;">
                <i class="bi bi-calendar-x"></i>
            </div>
            <div class="action-label">Apply Leave</div>
        </a>
        <!-- More actions -->
    </div>

    <!-- Stats -->
    <div class="grid-4 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ leave_balance }}</div>
            <div class="stat-label">Leave Days</div>
        </div>
        <!-- More stats -->
    </div>
</div>
```

### 2. Profile (`profile.html`)

**Key Changes:**
- Use `clean-card` for sections
- Simple form layouts with `form-label-clean` and `form-control-clean`
- Clean layout, no decorative elements

### 3. Payslip List (`payslip_list.html`)

**Key Changes:**
- Use `clean-table` for payslip list
- Use `badge-clean` for status
- Simple pagination with `pagination-clean`

**Example:**
```html
<div class="clean-card">
    <h6 class="section-title">Payslips</h6>
    <table class="clean-table">
        <thead>
            <tr>
                <th>Month</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for payslip in payslips %}
            <tr>
                <td>{{ payslip.month }}</td>
                <td>${{ payslip.amount }}</td>
                <td><span class="badge-clean badge-success">Paid</span></td>
                <td><a href="#" class="btn-clean-secondary btn-sm">View</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### 4. Document List (`document_list.html`)

**Key Changes:**
- Use `list-item` for document items
- Use `clean-card` wrapper
- Simple download buttons

### 5. Overtime Claims (`overtime_claim_list.html` & `overtime_claim_form.html`)

**Key Changes:**
- List: Use `clean-table`
- Form: Use `form-control-clean` and `form-label-clean`
- Simple layout like leave application form

### 6. Training Pages

**Key Changes:**
- Course cards: Use `clean-card`
- Course lists: Use `grid-3` or `grid-4`
- Progress indicators: Simple progress bars

## Color Palette

### Backgrounds
- **Primary:** `#ffffff` (white)
- **Secondary:** `#f9fafb` (light gray)
- **Subtle:** `#f3f4f6` (very light gray)

### Borders
- **Default:** `#e5e7eb`
- **Light:** `#f3f4f6`
- **Medium:** `#d1d5db`

### Text
- **Primary:** `#111827` (dark)
- **Secondary:** `#374151` (medium dark)
- **Muted:** `#6b7280` (gray)
- **Light:** `#9ca3af` (light gray)

### Status Colors
- **Success:** `#16a34a` / Background: `#dcfce7`
- **Warning:** `#d97706` / Background: `#fef3c7`
- **Danger:** `#dc2626` / Background: `#fee2e2`
- **Info:** `#3b82f6` / Background: `#dbeafe`

## Typography

### Font Sizes
- **Page Title:** 20px, weight 600
- **Section Title:** 14px, weight 600
- **Body Text:** 13px
- **Small Text:** 11px
- **Table Headers:** 11px, uppercase

### Font Weights
- **Bold:** 700
- **Semibold:** 600
- **Medium:** 500
- **Regular:** 400

## Spacing

### Margins & Padding
- **Small:** 8px
- **Compact:** 12px
- **Medium:** 16px
- **Large:** 24px

### Gaps
- **Grid gap:** 12px
- **Card margin:** 16px
- **Section spacing:** 24px

## Border Radius

- **Cards:** 8px
- **Small elements:** 6px
- **Buttons:** 6px
- **Badges:** 4px
- **Circles:** 50%

## Migration Checklist

For each page, follow this checklist:

- [ ] Include `employee-portal-clean.css`
- [ ] Replace custom styles with design system classes
- [ ] Convert gradients to simple backgrounds
- [ ] Update cards to use `clean-card`
- [ ] Update tables to use `clean-table`
- [ ] Update buttons to use `btn-clean-*`
- [ ] Update forms to use `form-*-clean`
- [ ] Update badges to use `badge-clean badge-*`
- [ ] Simplify layouts and reduce decorative elements
- [ ] Test responsiveness on mobile

## Benefits

1. **Consistency:** All pages look and feel the same
2. **Maintainability:** Single CSS file to update
3. **Performance:** Shared CSS caches across pages
4. **Speed:** Less CSS to load per page
5. **Simplicity:** Easy to understand and modify
6. **Accessibility:** Clean, readable design
7. **Professional:** Modern, clean appearance

## Next Steps

1. ✅ Design system CSS created
2. Include CSS in base template or individual pages
3. Update each employee portal page:
   - dashboard.html
   - profile.html
   - payslip_list.html
   - document_list.html
   - overtime_claim_list.html
   - overtime_claim_form.html
   - training pages
4. Test all pages for consistency
5. Remove old custom styles

---

**Note:** The attendance page (`attendance_list.html`) has already been updated with this design system and serves as a reference implementation.
