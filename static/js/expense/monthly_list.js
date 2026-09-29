(function () {
    'use strict';

    const page = document.getElementById('monthly-expense-page');
    const yearFilter = document.getElementById('year-filter');
    const monthFilter = document.getElementById('month-filter');
    const daysGrid = document.getElementById('days-grid');
    const editModal = document.getElementById('edit-modal');
    const editForm = document.getElementById('edit-form');
    const monthlyAddModal = document.getElementById('monthly-add-modal');
    const monthlyAddForm = document.getElementById('monthly-add-form');
    const today = new Date();
    let selectedYear = today.getFullYear();
    let selectedMonth = today.getMonth() + 1;
    let selectedDay = today.getDate();
    let editingRow = null;
    let monthData = [];

    function getUrl(template, values) {
        return template.replace(/0/g, () => values.shift());
    }

    function monthName(year, month) {
        return new Date(year, month - 1, 1).toLocaleDateString('en-US', { month: 'long' });
    }

    function getOrdinal(day) {
        if (day >= 11 && day <= 13) return `${day}th`;
        return `${day}${['th', 'st', 'nd', 'rd'][day % 10] || 'th'}`;
    }

    function updateHeadings(day) {
        const name = monthName(selectedYear, selectedMonth);
        const formattedDate = `${day} ${name} ${selectedYear}`;
        document.getElementById('monthly-heading').textContent = `${name} ${selectedYear} Overview`;
        document.getElementById('active-month-label').textContent = `${name} ${selectedYear}`;
        document.getElementById('selected-day-date').textContent = formattedDate;
    }

    function updateDaySummary(rowData) {
        document.getElementById('selected-day-total').textContent = `৳${Number(rowData.total || 0).toFixed(2)}`;
        document.getElementById('selected-day-items').textContent = rowData.count || 0;
    }

    function updateMonthlySummary(rows) {
        const total = rows.reduce((sum, row) => sum + Number(row.total || 0), 0);
        const activeDays = rows.filter((row) => Number(row.total) > 0).length;
        document.getElementById('monthly-total').textContent = `৳${total.toFixed(2)}`;
        document.getElementById('monthly-active-days').textContent = activeDays;
        document.getElementById('monthly-daily-average').textContent =
            `৳${(total / (rows.length || 1)).toFixed(2)}`;
    }

    function spendingLevel(total, maximum) {
        if (total <= 0 || maximum <= 0) return 0;
        const ratio = total / maximum;
        if (ratio <= 0.25) return 1;
        if (ratio <= 0.5) return 2;
        if (ratio <= 0.75) return 3;
        return 4;
    }

    function renderCalendar(rows) {
        daysGrid.replaceChildren();
        const firstWeekday = new Date(selectedYear, selectedMonth - 1, 1).getDay();
        const maximum = Math.max(...rows.map((row) => Number(row.total) || 0), 0);
        for (let index = 0; index < firstWeekday; index += 1) {
            const spacer = document.createElement('span');
            spacer.className = 'calendar-spacer';
            spacer.setAttribute('aria-hidden', 'true');
            daysGrid.appendChild(spacer);
        }

        rows.forEach((row) => {
            const amount = Number(row.total) || 0;
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'calendar-day';
            button.dataset.day = row.day;
            button.dataset.level = spendingLevel(amount, maximum);
            button.setAttribute('aria-pressed', String(row.day === selectedDay));
            button.setAttribute(
                'aria-label',
                `${monthName(selectedYear, selectedMonth)} ${row.day}: ৳${amount.toFixed(2)}, ${row.count} items`
            );

            const dayNumber = document.createElement('span');
            dayNumber.className = 'calendar-day-number';
            dayNumber.textContent = row.day;
            const total = document.createElement('span');
            total.className = 'calendar-day-total';
            total.textContent = amount ? `৳${amount.toFixed(0)}` : '—';
            const count = document.createElement('span');
            count.className = 'calendar-day-count';
            count.textContent = row.count ? `${row.count} item${row.count === 1 ? '' : 's'}` : '';
            button.append(dayNumber, total, count);
            daysGrid.appendChild(button);
        });
    }

    function updateEditTotal() {
        const price = parseFloat(document.getElementById('edit-price').value) || 0;
        const quantity = parseFloat(document.getElementById('edit-quantity').value) || 0;
        document.getElementById('edit-total').textContent = (price * quantity).toFixed(2);
    }

    function updateMonthlyAddTotal() {
        const price = parseFloat(document.getElementById('monthly-add-price').value) || 0;
        const quantity = parseFloat(document.getElementById('monthly-add-quantity').value) || 0;
        document.querySelector('#monthly-add-total span').textContent = (price * quantity).toFixed(2);
    }

    function openMonthlyAddModal() {
        monthlyAddForm.reset();
        document.getElementById('monthly-add-quantity').value = 1;
        document.getElementById('monthly-add-date').value = `${selectedYear}-${String(selectedMonth).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`;
        monthlyAddModal.style.display = 'flex';
        updateMonthlyAddTotal();
    }

    function closeMonthlyAddModal() {
        monthlyAddModal.style.display = 'none';
    }

    function openEditModal(row) {
        editingRow = row;
        const item = row.getData();
        document.getElementById('edit-id').value = item.id;
        document.getElementById('edit-name').value = item.name;
        document.getElementById('edit-price').value = item.price;
        document.getElementById('edit-quantity').value = item.quantity;
        document.getElementById('edit-location').value = item.location || '';
        document.getElementById('edit-date').value = item.date;
        document.getElementById('edit-description').value = item.description || '';
        updateEditTotal();
        editModal.style.display = 'flex';
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        editingRow = null;
    }

    async function submitRequest(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        return response.json();
    }

    const detailTable = new Tabulator('#detail-grid', {
        layout: 'fitColumns',
        height: '600px',
        placeholder: 'No expenses added for this day.',
        columns: [
            { title: 'Item', field: 'name' },
            { title: 'Price', field: 'price', hozAlign: 'right', formatter: 'money', formatterParams: { symbol: '৳ ', precision: 2 } },
            { title: 'Quantity', field: 'quantity', hozAlign: 'right' },
            { title: 'Location', field: 'location' },
            {
                title: 'Description',
                field: 'description',
                formatter: 'textarea',
                variableHeight: true,
                width: 220,
                minWidth: 160,
                widthGrow: 1,
                widthShrink: 1
            },
            { title: 'Total', field: 'total', hozAlign: 'right', formatter: 'money', formatterParams: { symbol: '৳ ', precision: 2 } },
            {
                title: 'Actions', width: 150, hozAlign: 'center',
                formatter: () => "<button class='btn-edit'>Edit</button> <button class='btn-delete'>Delete</button>",
                cellClick: (event, cell) => {
                    if (event.target.classList.contains('btn-edit')) openEditModal(cell.getRow());
                    if (event.target.classList.contains('btn-delete')) deleteExpense(cell.getRow());
                }
            }
        ]
    });

    async function loadDayDetails(day) {
        const url = getUrl(page.dataset.detailUrlTemplate, [selectedYear, selectedMonth, day]);
        await detailTable.setData(url);
    }

    async function loadMonth() {
        const response = await fetch(`${page.dataset.summaryUrl}?year=${selectedYear}&month=${selectedMonth}`);
        if (!response.ok) throw new Error('Could not load monthly expense summary.');
        const data = await response.json();
        monthData = data;
        selectedDay = Math.min(selectedDay, data.length || 1);
        updateMonthlySummary(data);
        renderCalendar(data);
        const selected = data.find((row) => row.day === selectedDay) || data[0];
        if (selected) await selectDay(selected);
    }

    async function selectDay(dayData) {
        selectedDay = dayData.day;
        daysGrid.querySelectorAll('.calendar-day').forEach((button) => {
            button.setAttribute('aria-pressed', String(Number(button.dataset.day) === selectedDay));
        });
        updateDaySummary(dayData);
        updateHeadings(selectedDay);
        await loadDayDetails(selectedDay);
    }

    function syncMonthControls() {
        yearFilter.value = selectedYear;
        monthFilter.value = selectedMonth;
        document.getElementById('previous-month').disabled = selectedYear === 2020 && selectedMonth === 1;
        const nextMonth = new Date(selectedYear, selectedMonth, 1);
        document.getElementById('next-month').disabled =
            nextMonth > new Date(today.getFullYear(), today.getMonth(), 1);
    }

    async function moveMonth(offset) {
        const nextDate = new Date(selectedYear, selectedMonth - 1 + offset, 1);
        if (nextDate.getFullYear() < 2020 || nextDate > new Date(today.getFullYear(), today.getMonth(), 1)) return;
        selectedYear = nextDate.getFullYear();
        selectedMonth = nextDate.getMonth() + 1;
        selectedDay = 1;
        syncMonthControls();
        await loadMonth();
    }

    async function deleteExpense(row) {
        const item = row.getData();
        if (!confirm(`Are you sure you want to delete "${item.name}"?`)) return;

        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        try {
            const url = page.dataset.deleteUrlTemplate.replace('/0/', `/${item.id}/`);
            const data = await submitRequest(url, formData);
            if (!data.success) return;
            await loadMonth();
        } catch (error) {
            console.error('Error deleting expense:', error);
        }
    }

    editForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const id = document.getElementById('edit-id').value;
        const formData = new FormData(editForm);
        ['name', 'price', 'quantity', 'location', 'date', 'description'].forEach((field) => {
            formData.append(field, document.getElementById(`edit-${field}`).value);
        });

        try {
            const url = page.dataset.editUrlTemplate.replace('/0/', `/${id}/`);
            const data = await submitRequest(url, formData);
            if (!data.success) {
                console.log(data.errors);
                return;
            }
            closeEditModal();
            await loadMonth();
        } catch (error) {
            console.error('Error updating expense:', error);
        }
    });

    monthlyAddForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        try {
            const data = await submitRequest(page.dataset.addUrl, new FormData(monthlyAddForm));
            if (!data.success) {
                console.log(data.errors);
                return;
            }
            closeMonthlyAddModal();
            await loadMonth();
        } catch (error) {
            console.error('Error adding daily expense:', error);
        }
    });

    daysGrid.addEventListener('click', async (event) => {
        const dayButton = event.target.closest('[data-day]');
        if (!dayButton) return;
        const dayData = monthData.find((row) => row.day === Number(dayButton.dataset.day));
        if (dayData) await selectDay(dayData);
    });

    yearFilter.addEventListener('change', async () => {
        selectedYear = parseInt(yearFilter.value, 10);
        selectedDay = 1;
        syncMonthControls();
        await loadMonth();
    });

    monthFilter.addEventListener('change', async () => {
        selectedMonth = parseInt(monthFilter.value, 10);
        selectedDay = 1;
        syncMonthControls();
        await loadMonth();
    });

    document.getElementById('previous-month').addEventListener('click', () => moveMonth(-1));
    document.getElementById('next-month').addEventListener('click', () => moveMonth(1));

    document.getElementById('edit-price').addEventListener('input', updateEditTotal);
    document.getElementById('edit-quantity').addEventListener('input', updateEditTotal);
    document.getElementById('monthly-add-price').addEventListener('input', updateMonthlyAddTotal);
    document.getElementById('monthly-add-quantity').addEventListener('input', updateMonthlyAddTotal);
    document.getElementById('open-monthly-add').addEventListener('click', openMonthlyAddModal);
    document.querySelectorAll('[data-close-monthly-add]').forEach((button) => {
        button.addEventListener('click', closeMonthlyAddModal);
    });
    document.querySelectorAll('[data-close-edit]').forEach((button) => {
        button.addEventListener('click', closeEditModal);
    });

    for (let year = today.getFullYear(); year >= 2020; year -= 1) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    }
    syncMonthControls();
    loadMonth().catch((error) => console.error('Error loading monthly expenses:', error));
}());