// Smart Search Functionality

class SmartSearch {
    constructor() {
        this.searchInput = document.getElementById('smartSearchInput');
        this.searchContainer = document.getElementById('smartSearchContainer');
        this.resultsDropdown = document.getElementById('searchResultsDropdown');
        this.resultsContent = document.getElementById('searchResultsContent');
        this.noResultsMessage = document.getElementById('noResultsMessage');
        this.searchFooter = document.getElementById('searchFooter');
        this.loadingSpinner = document.getElementById('searchLoadingSpinner');
        
        this.currentQuery = '';
        this.searchTimeout = null;
        this.selectedIndex = -1;
        this.results = [];
        this.isVisible = false;
        
        this.init();
    }
    
    init() {
        if (!this.searchInput) return;
        
        // Bind event listeners
        this.searchInput.addEventListener('input', this.handleInput.bind(this));
        this.searchInput.addEventListener('keydown', this.handleKeydown.bind(this));
        this.searchInput.addEventListener('focus', this.handleFocus.bind(this));
        
        // Close dropdown when clicking outside
        document.addEventListener('click', this.handleOutsideClick.bind(this));
        
        // Close dropdown on escape key
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
    }
    
    handleInput(event) {
        const query = event.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Reset selection
        this.selectedIndex = -1;
        
        // If query is too short, hide dropdown
        if (query.length < 2) {
            this.hideDropdown();
            return;
        }
        
        // Debounce search requests
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }
    
    handleFocus() {
        // Auto-close sidebar when search gets focus
        this.closeSidebar();

        if (this.results.length > 0 && this.searchInput.value.length >= 2) {
            this.showDropdown();
        }
    }

    closeSidebar() {
        const sidebar = document.querySelector('#sidebar');
        const mainContent = document.querySelector('#main-content');

        if (!sidebar) {
            return;
        }

        // Only close if sidebar is currently visible (not collapsed)
        if (!sidebar.classList.contains('collapsed')) {
            // Check if desktop or mobile
            if (window.innerWidth > 768) {
                // Desktop: collapse sidebar to 45px
                sidebar.classList.add('collapsed');

                // Adjust main content margin
                if (mainContent) {
                    mainContent.classList.add('sidebar-transitioning');
                    mainContent.style.marginLeft = '45px';

                    // Remove transition class after animation
                    setTimeout(() => {
                        mainContent.classList.remove('sidebar-transitioning');
                    }, 300);
                }

                // Save collapsed state
                localStorage.setItem('sidebarState', 'collapsed');
            } else {
                // Mobile: hide sidebar completely
                sidebar.classList.remove('mobile-open');

                // Hide overlay if exists
                const overlay = document.querySelector('#sidebar-overlay');
                if (overlay) overlay.classList.remove('active');

                // Restore body scroll
                document.body.style.overflow = '';
            }
        }
    }
    
    handleKeydown(event) {
        if (!this.isVisible || this.results.length === 0) return;
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
                this.updateSelection();
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
                
            case 'Enter':
                event.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectResult(this.results[this.selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.hideDropdown();
                this.searchInput.blur();
                break;
        }
    }
    
    handleOutsideClick(event) {
        if (!this.searchContainer.contains(event.target)) {
            this.hideDropdown();
        }
    }
    
    handleGlobalKeydown(event) {
        if (event.key === 'Escape') {
            this.hideDropdown();
        }
    }
    
    async performSearch(query) {
        if (query === this.currentQuery) return;
        
        this.currentQuery = query;
        this.showLoading();
        
        try {
            const response = await fetch(`/zone/ajax/smart-search/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.results = data.results || [];
            this.displayResults();
            
        } catch (error) {
            this.displayError();
        } finally {
            this.hideLoading();
        }
    }
    
    displayResults() {
        if (this.results.length === 0) {
            this.showNoResults();
            return;
        }
        
        this.resultsContent.innerHTML = '';
        this.noResultsMessage.classList.add('hidden');
        
        this.results.forEach((result, index) => {
            const resultElement = this.createResultElement(result, index);
            this.resultsContent.appendChild(resultElement);
        });
        
        this.showDropdown();
    }
    
    createResultElement(result, index) {
        const div = document.createElement('div');
        div.className = `search-result-item p-3 hover:bg-gray-50 cursor-pointer transition-colors duration-150`;
        div.dataset.index = index;

        // Add click handler
        div.addEventListener('click', () => this.selectResult(result));

        // Create type badge
        const typeBadge = this.createTypeBadge(result.type_class, result.type);

        // Create avatar or icon
        const avatarOrIcon = this.createAvatarOrIcon(result);

        // Build content
        div.innerHTML = `
            <div class="flex items-center space-x-3">
                ${avatarOrIcon}
                <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <p class="text-sm font-medium text-gray-900 truncate">
                                ${this.highlightMatch(result.title, this.currentQuery)}
                            </p>
                            ${typeBadge}
                        </div>
                        ${result.status ? `<span class="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">${result.status}</span>` : ''}
                    </div>
                    <p class="text-xs text-gray-500 truncate mt-1">
                        ${this.highlightMatch(result.subtitle, this.currentQuery)}
                    </p>
                </div>
                <div class="flex-shrink-0">
                    <i class="bi bi-arrow-right text-gray-400"></i>
                </div>
            </div>
        `;

        return div;
    }
    
    createTypeBadge(typeClass, typeText) {
        const colors = {
            'worker': 'bg-blue-100 text-blue-800',
            'vip': 'bg-purple-100 text-purple-800',
            'employee': 'bg-green-100 text-green-800',
            'menu': 'bg-orange-100 text-orange-800'
        };

        const color = colors[typeClass] || 'bg-gray-100 text-gray-800';

        return `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${color}">
            ${typeText}
        </span>`;
    }

    createAvatarOrIcon(result) {
        // For menu items, show an icon
        if (result.type_class === 'menu' && result.icon) {
            return `<div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
                <i class="${result.icon}"></i>
            </div>`;
        }

        // For people (workers/employees), show avatar
        return this.createAvatar(result.avatar, result.title);
    }

    createAvatar(avatarUrl, title) {
        if (avatarUrl) {
            return `<img class="w-8 h-8 rounded-full object-cover border" src="${avatarUrl}" alt="${title}" onerror="this.src='/static/images/default-avatar.svg'">`;
        } else {
            const initials = title.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
            return `<div class="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-xs font-medium text-gray-700">${initials}</div>`;
        }
    }
    
    highlightMatch(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>');
    }
    
    selectResult(result) {
        // Navigate to the result URL
        if (result.url) {
            window.location.href = result.url;
        }
        
        // Hide dropdown
        this.hideDropdown();
        
        // Clear search
        this.searchInput.value = '';
        this.currentQuery = '';
    }
    
    updateSelection() {
        // Remove previous selection
        this.resultsContent.querySelectorAll('.search-result-item').forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('bg-blue-50', 'border-l-4', 'border-blue-500');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('bg-blue-50', 'border-l-4', 'border-blue-500');
            }
        });
    }
    
    showDropdown() {
        this.resultsDropdown.classList.remove('hidden');
        this.searchFooter.classList.remove('hidden');
        this.isVisible = true;
    }
    
    hideDropdown() {
        this.resultsDropdown.classList.add('hidden');
        this.isVisible = false;
        this.selectedIndex = -1;
    }
    
    showNoResults() {
        this.resultsContent.innerHTML = '';
        this.noResultsMessage.classList.remove('hidden');
        this.searchFooter.classList.remove('hidden');
        this.showDropdown();
    }
    
    displayError() {
        this.resultsContent.innerHTML = `
            <div class="p-4 text-center text-red-500">
                <i class="bi bi-exclamation-triangle text-2xl mb-2"></i>
                <p class="text-sm">Search temporarily unavailable</p>
                <p class="text-xs text-gray-400">Please try again later</p>
            </div>
        `;
        this.searchFooter.classList.add('hidden');
        this.showDropdown();
    }
    
    showLoading() {
        this.loadingSpinner.classList.remove('hidden');
    }
    
    hideLoading() {
        this.loadingSpinner.classList.add('hidden');
    }
}

// Initialize smart search when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const smartSearch = new SmartSearch();
});