// Enhanced Date Picker for GuanYu Forms
// Usage: Include this file and call initializeDatePickers() in document.ready

let activeCalendar = null;
const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
const dayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

function initializeDatePickers() {
    // Initialize date pickers for all date input fields
    const dateInputs = document.querySelectorAll('.date-input-enhanced');
    
    dateInputs.forEach(input => {
        // Add click event to show calendar
        input.addEventListener('click', function() {
            const fieldId = this.id;
            showCalendar(fieldId);
        });
        
        // Initialize calendar for this field
        const fieldId = input.id;
        initializeCalendar(fieldId);
    });
    
    // Close calendar when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.date-input-container')) {
            hideAllCalendars();
        }
    });
    
    // Handle keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (activeCalendar && (e.key === 'Escape')) {
            hideAllCalendars();
        }
    });
}

function initializeCalendar(fieldId) {
    const input = document.getElementById(fieldId);
    const hiddenInput = document.getElementById(fieldId + '_hidden');
    
    if (!input) return;
    
    // Set initial date if available
    let initialDate = null;
    if (hiddenInput && hiddenInput.value && hiddenInput.value.trim() !== '') {
        // Parse the date value (should be in YYYY-MM-DD format)
        const dateValue = hiddenInput.value.trim();
        initialDate = new Date(dateValue + 'T00:00:00'); // Add time to avoid timezone issues
        
        // Validate the parsed date
        if (isNaN(initialDate.getTime())) {
            initialDate = null;
        }
    }
    
    // Store calendar state
    const calendarState = {
        currentDate: new Date(),
        selectedDate: initialDate,
        viewDate: initialDate ? new Date(initialDate) : new Date()
    };
    
    // Store state on the input element
    input.calendarState = calendarState;
    
    // Update display input if we have a valid initial date
    if (initialDate) {
        input.value = formatDisplayDate(initialDate);
    }
}

function showCalendar(fieldId) {
    try {
        // Hide all other calendars first
        hideAllCalendars();
        
        const input = document.getElementById(fieldId);
        const calendar = document.getElementById('date-picker-' + fieldId);

        if (!input) {
            return;
        }

        if (!calendar) {
            return;
        }
        
        // Initialize calendar if not already initialized
        if (!input.calendarState) {
            initializeCalendar(fieldId);
        }
        
        calendar.style.display = 'block';
        activeCalendar = fieldId;
        
        // Render calendar with current state
        renderCalendar(fieldId);
    } catch (error) {
    }
}

function hideAllCalendars() {
    const calendars = document.querySelectorAll('.date-picker-calendar');
    calendars.forEach(calendar => {
        calendar.style.display = 'none';
    });
    activeCalendar = null;
}

function renderCalendar(fieldId) {
    const input = document.getElementById(fieldId);
    const gridElement = document.getElementById('calendar-grid-' + fieldId);
    const monthSelect = document.getElementById('month-select-' + fieldId);
    const yearSelect = document.getElementById('year-select-' + fieldId);
    
    if (!input || !input.calendarState || !gridElement || !monthSelect || !yearSelect) {
        return;
    }
    
    const state = input.calendarState;
    const viewDate = state.viewDate;
    
    // Validate viewDate
    if (!viewDate || isNaN(viewDate.getTime())) {
        state.viewDate = new Date(); // Reset to current date
        return;
    }
    
    // Populate month dropdown
    populateMonthSelect(monthSelect, viewDate.getMonth());
    
    // Populate year dropdown with appropriate range
    populateYearSelect(yearSelect, viewDate.getFullYear(), fieldId);
    
    // Clear grid
    gridElement.innerHTML = '';
    
    // Add day headers
    dayNames.forEach(day => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'date-picker-day-header';
        dayHeader.textContent = day;
        gridElement.appendChild(dayHeader);
    });
    
    // Get first day of month and number of days
    const firstDay = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1);
    const lastDay = new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    // Add previous month's trailing days
    const prevMonth = new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 0);
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
        const dayElement = createDayElement(prevMonth.getDate() - i, fieldId, true, false);
        gridElement.appendChild(dayElement);
    }
    
    // Add current month's days
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const dayDate = new Date(viewDate.getFullYear(), viewDate.getMonth(), day);
        const isToday = (dayDate.toDateString() === today.toDateString());
        const isSelected = state.selectedDate && !isNaN(state.selectedDate.getTime()) && (dayDate.toDateString() === state.selectedDate.toDateString());
        
        const dayElement = createDayElement(day, fieldId, false, isToday, isSelected);
        gridElement.appendChild(dayElement);
    }
    
    // Add next month's leading days
    const remainingCells = 42 - (startingDayOfWeek + daysInMonth); // 6 rows * 7 days = 42
    for (let day = 1; day <= remainingCells && remainingCells < 7; day++) {
        const dayElement = createDayElement(day, fieldId, true, false);
        gridElement.appendChild(dayElement);
    }
}

function createDayElement(day, fieldId, isOtherMonth, isToday, isSelected) {
    const dayElement = document.createElement('div');
    dayElement.className = 'date-picker-day';
    dayElement.textContent = day;
    
    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    }
    if (isToday) {
        dayElement.classList.add('today');
    }
    if (isSelected) {
        dayElement.classList.add('selected');
    }
    
    // Add click event
    if (!isOtherMonth) {
        dayElement.addEventListener('click', function() {
            selectDate(fieldId, day);
        });
    }
    
    return dayElement;
}

function navigateMonth(fieldId, direction) {
    const input = document.getElementById(fieldId);
    if (!input || !input.calendarState) return;
    
    const state = input.calendarState;
    state.viewDate.setMonth(state.viewDate.getMonth() + direction);
    
    renderCalendar(fieldId);
}

function selectDate(fieldId, day) {
    try {
        const input = document.getElementById(fieldId);
        const hiddenInput = document.getElementById(fieldId + '_hidden');
        
        if (!input || !input.calendarState) {
            return;
        }
        
        const state = input.calendarState;
        
        // Validate viewDate before using it
        if (!state.viewDate || isNaN(state.viewDate.getTime())) {
            state.viewDate = new Date(); // Reset to current date
        }
        
        const selectedDate = new Date(state.viewDate.getFullYear(), state.viewDate.getMonth(), day);
        
        // Validate the created date
        if (isNaN(selectedDate.getTime())) {
            return;
        }
        
        // Update state
        state.selectedDate = selectedDate;
        
        // Format and display date
        const formattedDate = formatDisplayDate(selectedDate);
        input.value = formattedDate;
        
        // Update hidden input with ISO format for form submission
        if (hiddenInput) {
            hiddenInput.value = selectedDate.toISOString().split('T')[0];
        }
        
        // Hide calendar
        hideAllCalendars();
        
        // Trigger change event for form validation
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Special handling for specific field types
        if (fieldId.includes('dob') && typeof updateAgeDisplay === 'function') {
            updateAgeDisplay();
        }
    } catch (error) {
    }
}

function selectToday(fieldId) {
    const today = new Date();
    const input = document.getElementById(fieldId);
    
    if (!input || !input.calendarState) return;
    
    // Update view to current month
    input.calendarState.viewDate = new Date(today);
    renderCalendar(fieldId);
    
    // Select today's date
    selectDate(fieldId, today.getDate());
}

function clearDate(fieldId) {
    const input = document.getElementById(fieldId);
    const hiddenInput = document.getElementById(fieldId + '_hidden');
    
    if (!input) return;
    
    // Clear display input
    input.value = '';
    
    // Clear hidden input
    if (hiddenInput) {
        hiddenInput.value = '';
    }
    
    // Update state
    if (input.calendarState) {
        input.calendarState.selectedDate = null;
        renderCalendar(fieldId);
    }
    
    // Hide calendar
    hideAllCalendars();
    
    // Trigger change event
    input.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Special handling for specific field types
    if (fieldId.includes('dob') && typeof updateAgeDisplay === 'function') {
        updateAgeDisplay();
    }
}

function formatDisplayDate(date) {
    // Validate input
    if (!date || isNaN(date.getTime())) {
        return ''; 
    }
    
    // Format as "15/Jan/2024"
    const day = date.getDate();
    const month = monthNames[date.getMonth()].substring(0, 3);
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

// Helper function to populate month dropdown
function populateMonthSelect(monthSelect, selectedMonth) {
    monthSelect.innerHTML = '';
    
    monthNames.forEach((month, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = month;
        option.selected = index === selectedMonth;
        monthSelect.appendChild(option);
    });
}

// Helper function to populate year dropdown with smart ranges
function populateYearSelect(yearSelect, selectedYear, fieldId) {
    yearSelect.innerHTML = '';
    
    let startYear, endYear;
    
    // Determine year range based on field type
    if (fieldId.includes('dob') || fieldId.includes('date_of_birth')) {
        // For date of birth: 1900 to current year
        startYear = 1900;
        endYear = new Date().getFullYear();
    } else if (fieldId.includes('hire_date') || fieldId.includes('end_date') || fieldId.includes('membership')) {
        // For employment/membership dates: current year - 10 to current year + 5
        const currentYear = new Date().getFullYear();
        startYear = currentYear - 10;
        endYear = currentYear + 5;
    } else {
        // Default range: current year - 50 to current year + 10
        const currentYear = new Date().getFullYear();
        startYear = currentYear - 50;
        endYear = currentYear + 10;
    }
    
    // Ensure selected year is included in range
    if (selectedYear < startYear) startYear = selectedYear;
    if (selectedYear > endYear) endYear = selectedYear;
    
    // Populate dropdown (newest years first for date of birth)
    if (fieldId.includes('dob') || fieldId.includes('date_of_birth')) {
        // For date of birth, show newest years first
        for (let year = endYear; year >= startYear; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            option.selected = year === selectedYear;
            yearSelect.appendChild(option);
        }
    } else {
        // For other dates, show oldest years first
        for (let year = startYear; year <= endYear; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            option.selected = year === selectedYear;
            yearSelect.appendChild(option);
        }
    }
}

// Handler for month/year dropdown changes
function changeMonthYear(fieldId) {
    const input = document.getElementById(fieldId);
    const monthSelect = document.getElementById('month-select-' + fieldId);
    const yearSelect = document.getElementById('year-select-' + fieldId);
    
    if (!input || !input.calendarState || !monthSelect || !yearSelect) return;
    
    const state = input.calendarState;
    const newMonth = parseInt(monthSelect.value);
    const newYear = parseInt(yearSelect.value);
    
    // Update view date
    state.viewDate = new Date(newYear, newMonth, 1);
    
    // Re-render calendar
    renderCalendar(fieldId);
}