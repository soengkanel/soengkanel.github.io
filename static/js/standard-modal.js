/**
 * Standard Modal JavaScript
 *
 * This file provides consistent modal behavior across the application.
 * Handles:
 * - Backdrop z-index management
 * - Fixed center positioning enforcement
 * - Interactive element activation
 * - Keyboard navigation
 *
 * Usage: Include this JS file after Bootstrap in your base template.
 */

(function() {
    'use strict';

    console.log('📦 Standard Modal JS: Initializing...');

    /**
     * Fix backdrop z-index for a specific modal
     * @param {HTMLElement} modalElement - The modal DOM element
     * @param {number} backdropZIndex - The z-index to set for the backdrop
     * @param {string} modalName - Name for logging
     */
    function fixModalBackdrop(modalElement, backdropZIndex, modalName) {
        let backdropFixed = false;

        // Create observer to watch for backdrop creation
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('modal-backdrop') && !backdropFixed) {
                        console.log(`🎭 ${modalName}: Backdrop detected, fixing...`);

                        // Mark as fixed
                        backdropFixed = true;

                        // Disconnect to prevent loop
                        observer.disconnect();

                        // Move backdrop BEFORE modal in DOM
                        if (modalElement.parentNode && modalElement.parentNode.contains(node)) {
                            modalElement.parentNode.insertBefore(node, modalElement);
                            console.log(`✅ ${modalName}: Backdrop moved before modal`);
                        }

                        // Set z-index
                        node.style.setProperty('z-index', backdropZIndex.toString(), 'important');
                        node.style.setProperty('pointer-events', 'auto', 'important');

                        console.log(`✅ ${modalName}: Backdrop z-index set to ${backdropZIndex}`);
                    }
                });
            });
        });

        // Start observing on modal show
        modalElement.addEventListener('show.bs.modal', function() {
            backdropFixed = false;
            observer.observe(document.body, { childList: true });
            console.log(`👀 ${modalName}: Watching for backdrop...`);

            // Set modal z-index
            const modalZIndex = backdropZIndex + 5;
            modalElement.style.setProperty('z-index', modalZIndex.toString(), 'important');

            // Fix existing backdrop immediately
            setTimeout(() => {
                const existingBackdrop = document.querySelector('.modal-backdrop');
                if (existingBackdrop) {
                    console.log(`🔧 ${modalName}: Found existing backdrop, fixing...`);

                    if (modalElement.parentNode) {
                        modalElement.parentNode.insertBefore(existingBackdrop, modalElement);
                    }

                    existingBackdrop.style.setProperty('z-index', backdropZIndex.toString(), 'important');
                    console.log(`✅ ${modalName}: Existing backdrop fixed`);
                }
            }, 10);
        });

        // Stop observing and verify after modal shown
        modalElement.addEventListener('shown.bs.modal', function() {
            setTimeout(() => {
                observer.disconnect();
                console.log(`👀 ${modalName}: Stopped watching`);

                // Double-check backdrop z-index
                const backdrop = document.querySelector('.modal-backdrop.show');
                if (backdrop) {
                    const backdropZ = window.getComputedStyle(backdrop).zIndex;
                    const modalZ = window.getComputedStyle(modalElement).zIndex;
                    console.log(`🔍 ${modalName}: Backdrop z-index: ${backdropZ}, Modal z-index: ${modalZ}`);

                    if (parseInt(backdropZ) >= parseInt(modalZ)) {
                        console.warn(`⚠️ ${modalName}: Backdrop z-index too high! Forcing fix...`);
                        backdrop.style.setProperty('z-index', backdropZIndex.toString(), 'important');
                    }
                }
            }, 100);

            // Ensure modal container uses flexbox centering
            modalElement.style.setProperty('display', 'flex', 'important');
            modalElement.style.setProperty('align-items', 'center', 'important');
            modalElement.style.setProperty('justify-content', 'center', 'important');

            // Ensure modal dialog is positioned correctly
            const modalDialog = modalElement.querySelector('.modal-dialog');
            if (modalDialog) {
                modalDialog.style.setProperty('position', 'relative', 'important');
                modalDialog.style.setProperty('margin', 'auto', 'important');
                modalDialog.style.setProperty('transform', 'none', 'important');
                console.log(`✅ ${modalName}: Dialog centered with flexbox`);
            }

            // Ensure all interactive elements are clickable
            const allInteractive = modalElement.querySelectorAll('input, select, textarea, button, a');
            allInteractive.forEach(element => {
                element.style.setProperty('pointer-events', 'auto', 'important');
            });

            console.log(`✅ ${modalName}: All interactive elements enabled`);
        });

        // Add keyboard navigation
        modalElement.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        });

        // Fix ARIA attributes before modal hides
        modalElement.addEventListener('hide.bs.modal', function() {
            // Remove aria-hidden to prevent accessibility warning
            modalElement.removeAttribute('aria-hidden');
            console.log(`✅ ${modalName}: ARIA attributes cleared before hide`);
        });

        // Restore ARIA attributes after modal is hidden
        modalElement.addEventListener('hidden.bs.modal', function() {
            // Restore aria-hidden after modal is completely hidden
            modalElement.setAttribute('aria-hidden', 'true');

            // Remove focus from modal
            if (document.activeElement === modalElement) {
                document.activeElement.blur();
            }

            console.log(`✅ ${modalName}: ARIA attributes restored after hide`);
        });
    }

    /**
     * Initialize all modals with standard behavior
     */
    function initializeStandardModals() {
        // Modal configuration: [selector, backdropZIndex, name]
        const modalsConfig = [
            // Level 1 - Base modals
            { selector: '.modal-level-1', backdropZIndex: 1055, name: 'Level 1 Modal' },

            // Level 2 - View modals
            { selector: '.modal-level-2', backdropZIndex: 1065, name: 'Level 2 Modal' },
            { selector: '#viewOvertimeModal', backdropZIndex: 1065, name: 'View Overtime Modal' },
            { selector: '#editModal', backdropZIndex: 1065, name: 'Edit Modal' },

            // Level 3 - Action modals
            { selector: '.modal-level-3', backdropZIndex: 1075, name: 'Level 3 Modal' },
            { selector: '#approveOvertimeModal', backdropZIndex: 1075, name: 'Approve Modal' },
            { selector: '#rejectOvertimeModal', backdropZIndex: 1075, name: 'Reject Modal' },

            // Level 4 - Critical modals
            { selector: '.modal-level-4', backdropZIndex: 1085, name: 'Level 4 Modal' },
            { selector: '#deleteModal', backdropZIndex: 1085, name: 'Delete Modal' }
        ];

        let initializedCount = 0;

        modalsConfig.forEach(config => {
            const modals = document.querySelectorAll(config.selector);
            modals.forEach(modal => {
                fixModalBackdrop(modal, config.backdropZIndex, config.name);
                initializedCount++;
            });
        });

        console.log(`✅ Standard Modal JS: Initialized ${initializedCount} modal(s)`);
    }

    /**
     * Auto-initialize on DOM ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeStandardModals);
    } else {
        initializeStandardModals();
    }

    // Export for manual initialization if needed
    window.StandardModal = {
        init: initializeStandardModals,
        fixBackdrop: fixModalBackdrop
    };

})();
