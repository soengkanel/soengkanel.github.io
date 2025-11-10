/**
 * Worker Search Autocomplete for Probation Form
 * Provides real-time search suggestions for workers when creating probation periods
 */

class WorkerProbationSearch {
    constructor() {
        this.searchField = document.getElementById('id_worker_search');
        this.workerField = document.getElementById('id_worker');
        this.suggestionsContainer = null;
        this.currentTimeout = null;
        this.minQueryLength = 2;
        this.searchDelay = 300; // ms
        
        this.init();
    }
    
    init() {
        if (!this.searchField) {
            return;
        }
        
        this.createSuggestionsContainer();
        this.bindEvents();
        this.styleSearchField();
    }
    
    createSuggestionsContainer() {
        this.suggestionsContainer = document.createElement('div');
        this.suggestionsContainer.className = 'worker-search-suggestions';
        this.suggestionsContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #d1d5db;
            border-top: none;
            border-radius: 0 0 6px 6px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        `;
        
        // Make parent container relative
        const parentDiv = this.searchField.parentElement;
        parentDiv.style.position = 'relative';
        parentDiv.appendChild(this.suggestionsContainer);
    }
    
    styleSearchField() {
        // Add search icon styling
        this.searchField.style.paddingLeft = '38px';
        this.searchField.placeholder = 'Search worker by name, ID, or nickname...';
        
        // Add search icon if not already present
        const existingIcon = this.searchField.parentElement.querySelector('.search-icon');
        if (!existingIcon) {
            const searchIcon = document.createElement('i');
            searchIcon.className = 'bi bi-search search-icon';
            searchIcon.style.cssText = `
                position: absolute;
                left: 12px;
                top: 50%;
                transform: translateY(-50%);
                color: #9ca3af;
                pointer-events: none;
                z-index: 1;
            `;
            
            const parentDiv = this.searchField.parentElement;
            parentDiv.insertBefore(searchIcon, this.searchField);
        }
    }
    
    bindEvents() {
        // Search input event
        this.searchField.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.searchField.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
        
        // Handle keyboard navigation
        this.searchField.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e);
        });
    }
    
    handleSearch(query) {
        // Clear existing timeout
        if (this.currentTimeout) {
            clearTimeout(this.currentTimeout);
        }
        
        // Hide suggestions if query is too short
        if (query.length < this.minQueryLength) {
            this.hideSuggestions();
            return;
        }
        
        // Debounce the search
        this.currentTimeout = setTimeout(() => {
            this.performSearch(query);
        }, this.searchDelay);
    }
    
    async performSearch(query) {
        try {
            this.showLoading();
            
            const response = await fetch(`/zone/api/worker-search-probation/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displaySuggestions(data.workers);
            } else {
                throw new Error('Search failed');
            }
        } catch (error) {
            this.showError('Search failed. Please try again.');
        }
    }
    
    showLoading() {
        this.suggestionsContainer.innerHTML = `
            <div class="worker-suggestion-item loading">
                <i class="bi bi-arrow-repeat spin"></i> Searching...
            </div>
        `;
        this.suggestionsContainer.style.display = 'block';
    }
    
    showError(message) {
        this.suggestionsContainer.innerHTML = `
            <div class="worker-suggestion-item error">
                <i class="bi bi-exclamation-triangle"></i> ${message}
            </div>
        `;
        this.suggestionsContainer.style.display = 'block';
    }
    
    displaySuggestions(workers) {
        if (!workers || workers.length === 0) {
            this.suggestionsContainer.innerHTML = `
                <div class="worker-suggestion-item no-results">
                    <i class="bi bi-search"></i> No workers found
                </div>
            `;
        } else {
            this.suggestionsContainer.innerHTML = workers.map(worker => `
                <div class="worker-suggestion-item" data-worker-id="${worker.worker_id}">
                    <div class="worker-info">
                        <div class="worker-name">${worker.worker_name}</div>
                        <div class="worker-details">
                            ID: ${worker.worker_code} | ${worker.position} | ${worker.zone}
                            ${worker.has_active_probation ? '<span class="badge bg-warning text-dark">Has Active Probation</span>' : ''}
                        </div>
                    </div>
                </div>
            `).join('');
            
            // Bind click events to suggestions
            this.bindSuggestionEvents();
        }
        
        this.suggestionsContainer.style.display = 'block';
    }
    
    bindSuggestionEvents() {
        const suggestionItems = this.suggestionsContainer.querySelectorAll('.worker-suggestion-item[data-worker-id]');
        
        suggestionItems.forEach(item => {
            item.addEventListener('click', () => {
                const workerId = item.dataset.workerId;
                const workerName = item.querySelector('.worker-name').textContent;
                
                this.selectWorker(workerId, workerName);
            });
            
            // Hover effect
            item.addEventListener('mouseenter', () => {
                this.clearHighlight();
                item.classList.add('highlighted');
            });
        });
    }
    
    selectWorker(workerId, workerName) {
        // Set the hidden worker field
        if (this.workerField) {
            this.workerField.value = workerId;
        }
        
        // Set the search field display text
        this.searchField.value = workerName;
        
        // Hide suggestions
        this.hideSuggestions();
        
        // Optional: Trigger change event for form validation
        this.searchField.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
    }
    
    handleKeyNavigation(e) {
        const suggestions = this.suggestionsContainer.querySelectorAll('.worker-suggestion-item[data-worker-id]');
        
        if (suggestions.length === 0) return;
        
        const highlighted = this.suggestionsContainer.querySelector('.highlighted');
        let currentIndex = highlighted ? Array.from(suggestions).indexOf(highlighted) : -1;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = currentIndex < suggestions.length - 1 ? currentIndex + 1 : 0;
                this.highlightSuggestion(suggestions[currentIndex]);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = currentIndex > 0 ? currentIndex - 1 : suggestions.length - 1;
                this.highlightSuggestion(suggestions[currentIndex]);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (highlighted) {
                    highlighted.click();
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }
    
    highlightSuggestion(suggestion) {
        this.clearHighlight();
        suggestion.classList.add('highlighted');
        
        // Scroll into view if needed
        suggestion.scrollIntoView({ block: 'nearest' });
    }
    
    clearHighlight() {
        const highlighted = this.suggestionsContainer.querySelector('.highlighted');
        if (highlighted) {
            highlighted.classList.remove('highlighted');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new WorkerProbationSearch();
});

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
    .worker-suggestion-item {
        padding: 12px 16px;
        border-bottom: 1px solid #f3f4f6;
        cursor: pointer;
        transition: background-color 0.15s ease;
    }
    
    .worker-suggestion-item:last-child {
        border-bottom: none;
    }
    
    .worker-suggestion-item:hover,
    .worker-suggestion-item.highlighted {
        background-color: #f8fafc;
    }
    
    .worker-suggestion-item.loading,
    .worker-suggestion-item.error,
    .worker-suggestion-item.no-results {
        text-align: center;
        color: #6b7280;
        cursor: default;
        font-style: italic;
    }
    
    .worker-suggestion-item.error {
        color: #dc2626;
    }
    
    .worker-info .worker-name {
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 2px;
    }
    
    .worker-info .worker-details {
        font-size: 12px;
        color: #6b7280;
    }
    
    .worker-info .badge {
        font-size: 9px;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
    }
    
    .spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);