/**
 * Reusable Autocomplete Component
 * Usage:
 *
 * const autocomplete = new Autocomplete({
 *   inputSelector: '#my-input',
 *   data: [{id: 1, name: 'John Doe', email: 'john@example.com'}, ...],
 *   displayField: 'name',
 *   searchFields: ['name', 'email'],
 *   minChars: 0,
 *   maxResults: 50,
 *   onSelect: (item) => { }
 * });
 */

class Autocomplete {
    constructor(options) {
        this.options = {
            inputSelector: options.inputSelector,
            data: options.data || [],
            displayField: options.displayField || 'name',
            searchFields: options.searchFields || ['name'],
            valueField: options.valueField || 'id',
            minChars: options.minChars !== undefined ? options.minChars : 0,
            maxResults: options.maxResults || 50,
            placeholder: options.placeholder || 'Type to search...',
            noResultsText: options.noResultsText || 'No results found',
            onSelect: options.onSelect || (() => {}),
            renderItem: options.renderItem || this.defaultRenderItem.bind(this),
            container: options.container || null,
        };

        this.input = document.querySelector(this.options.inputSelector);
        if (!this.input) {
            return;
        }

        this.selectedIndex = -1;
        this.selectedItem = null;
        this.init();
    }

    init() {
        // Create hidden input for storing selected value
        this.hiddenInput = document.createElement('input');
        this.hiddenInput.type = 'hidden';
        this.hiddenInput.name = this.input.name ? `${this.input.name}_id` : '';
        this.input.parentNode.insertBefore(this.hiddenInput, this.input.nextSibling);

        // Create dropdown container
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.display = 'none';

        // Insert dropdown after input
        if (this.options.container) {
            this.options.container.style.position = 'relative';
            this.options.container.appendChild(this.dropdown);
        } else {
            this.input.parentNode.style.position = 'relative';
            this.input.parentNode.appendChild(this.dropdown);
        }

        // Set up event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Input events
        this.input.addEventListener('focus', () => this.handleFocus());
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    handleFocus() {
        if (this.input.value.length >= this.options.minChars) {
            this.filterAndShow(this.input.value);
        } else if (this.options.minChars === 0) {
            this.filterAndShow('');
        }
    }

    handleInput(e) {
        const query = e.target.value;
        this.hiddenInput.value = ''; // Clear hidden value when typing
        this.selectedItem = null;

        if (query.length >= this.options.minChars) {
            this.filterAndShow(query);
        } else if (this.options.minChars === 0 && query.length === 0) {
            this.filterAndShow('');
        } else {
            this.hideDropdown();
        }
    }

    handleKeydown(e) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection(items);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(items);
                break;

            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
                    this.selectItem(items[this.selectedIndex].dataset.index);
                }
                break;

            case 'Escape':
                this.hideDropdown();
                break;

            case 'Tab':
                if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
                    e.preventDefault();
                    this.selectItem(items[this.selectedIndex].dataset.index);
                }
                this.hideDropdown();
                break;
        }
    }

    handleBlur(e) {
        // Delay to allow click events on dropdown items
        setTimeout(() => {
            if (!this.dropdown.contains(document.activeElement)) {
                this.hideDropdown();
            }
        }, 200);
    }

    filterAndShow(query) {
        query = query.toLowerCase();

        // Filter data based on search fields
        let filtered = this.options.data.filter(item => {
            return this.options.searchFields.some(field => {
                const value = this.getNestedValue(item, field);
                return value && value.toString().toLowerCase().includes(query);
            });
        });

        // Limit results
        filtered = filtered.slice(0, this.options.maxResults);

        this.renderDropdown(filtered);
        this.showDropdown();
    }

    renderDropdown(items) {
        if (items.length === 0) {
            this.dropdown.innerHTML = `<div class="autocomplete-no-results">${this.options.noResultsText}</div>`;
            return;
        }

        this.dropdown.innerHTML = items.map((item, index) => {
            return this.options.renderItem(item, index);
        }).join('');

        // Attach click handlers
        this.dropdown.querySelectorAll('.autocomplete-item').forEach((element, index) => {
            element.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Prevent input blur
                this.selectItem(index);
            });
        });

        this.selectedIndex = -1;
    }

    defaultRenderItem(item, index) {
        const displayValue = this.getNestedValue(item, this.options.displayField);
        const secondaryFields = this.options.searchFields.filter(f => f !== this.options.displayField);
        const secondaryValue = secondaryFields.length > 0
            ? this.getNestedValue(item, secondaryFields[0])
            : '';

        return `
            <div class="autocomplete-item" data-index="${index}">
                <div class="autocomplete-item-name">${this.escapeHtml(displayValue)}</div>
                ${secondaryValue ? `<div class="autocomplete-item-email">${this.escapeHtml(secondaryValue)}</div>` : ''}
            </div>
        `;
    }

    selectItem(index) {
        const filtered = this.getFilteredData();
        const item = filtered[index];

        if (!item) return;

        this.selectedItem = item;
        this.input.value = this.getNestedValue(item, this.options.displayField);
        this.hiddenInput.value = this.getNestedValue(item, this.options.valueField);

        this.hideDropdown();
        this.options.onSelect(item);
    }

    getFilteredData() {
        const query = this.input.value.toLowerCase();
        return this.options.data.filter(item => {
            return this.options.searchFields.some(field => {
                const value = this.getNestedValue(item, field);
                return value && value.toString().toLowerCase().includes(query);
            });
        }).slice(0, this.options.maxResults);
    }

    updateSelection(items) {
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    showDropdown() {
        this.dropdown.style.display = 'block';
        this.dropdown.classList.add('show');
    }

    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.dropdown.classList.remove('show');
        this.selectedIndex = -1;
    }

    // Helper methods
    getNestedValue(obj, path) {
        return path.split('.').reduce((acc, part) => acc && acc[part], obj);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public methods
    setData(data) {
        this.options.data = data;
        if (this.dropdown.style.display !== 'none') {
            this.filterAndShow(this.input.value);
        }
    }

    getValue() {
        return this.hiddenInput.value;
    }

    getSelectedItem() {
        return this.selectedItem;
    }

    clear() {
        this.input.value = '';
        this.hiddenInput.value = '';
        this.selectedItem = null;
        this.hideDropdown();
    }

    destroy() {
        this.dropdown.remove();
        this.hiddenInput.remove();
    }
}

// Export for use in modules or make globally available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Autocomplete;
} else {
    window.Autocomplete = Autocomplete;
}
