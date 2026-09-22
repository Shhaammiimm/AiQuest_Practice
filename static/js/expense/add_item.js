(function () {
    'use strict';

    const page = document.getElementById('expense-page');
    const expenseForm = document.getElementById('expense-form');
    const editForm = document.getElementById('edit-form');
    const editModal = document.getElementById('edit-modal');
    const recentExpenses = JSON.parse(
        document.getElementById('recent-expenses-data').textContent
    );
    let editingRow = null;

    function getNumber(id) {
        return parseFloat(document.getElementById(id).value) || 0;
    }

    function updateTotal() {
        document.getElementById('total-preview').textContent =
            (getNumber('id_price') * getNumber('id_quantity')).toFixed(2);
    }

    function updateEditTotal() {
        document.getElementById('edit-total').textContent =
            (getNumber('edit-price') * getNumber('edit-quantity')).toFixed(2);
    }

    function getTodayDate() {
        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${now.getFullYear()}-${month}-${day}`;
    }

    function updateTodayTotal(rows) {
        const today = getTodayDate();
        const total = rows.reduce((sum, item) => {
            if (item.date !== today) return sum;
            return sum + (Number(item.total) || 0);
        }, 0);

        document.getElementById('today-total-expense').textContent =
            `৳${total.toFixed(2)}`;
    }

    function createTable() {
        return new Tabulator('#recent-expense-grid', {
            data: recentExpenses,
            layout: 'fitColumns',
            placeholder: 'No expenses added in the last 24 hours.',
            columns: [
                { title: '#', formatter: 'rownum', width: 55, hozAlign: 'center' },
                { title: 'Item', field: 'name' },
                {
                    title: 'Price', field: 'price', hozAlign: 'right',
                    formatter: 'money', formatterParams: { symbol: '৳ ' }
                },
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
                {
                    title: 'Total', field: 'total', hozAlign: 'right',
                    formatter: 'money', formatterParams: { symbol: '৳ ' }
                },
                { title: 'Expense Date', field: 'date' },
                {
                    title: 'Edit', width: 80, hozAlign: 'center',
                    formatter: () => "<button class='btn-edit'>Edit</button>",
                    cellClick: (event, cell) => openEditModal(cell.getRow())
                },
                {
                    title: 'Delete', width: 90, hozAlign: 'center',
                    formatter: () => "<button class='btn-delete'>Delete</button>",
                    cellClick: (event, cell) => confirmDelete(cell.getRow())
                }
            ]
        });
    }

    function openEditModal(row) {
        editingRow = row;
        const item = row.getData();

        document.getElementById('edit-id').value = item.id;
        document.getElementById('edit-name').value = item.name;
        document.getElementById('edit-price').value = item.price;
        document.getElementById('edit-quantity').value = item.quantity;
        document.getElementById('edit-location').value = item.location;
        document.getElementById('edit-date').value = item.date;
        document.getElementById('edit-description').value = item.description || '';
        updateEditTotal();
        editModal.style.display = 'flex';
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        editingRow = null;
    }

    async function submitForm(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        return response.json();
    }

    expenseForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        try {
            const data = await submitForm(page.dataset.addUrl, new FormData(expenseForm));
            if (!data.success) {
                console.log(data.errors);
                return;
            }

            todayTable.addRow(data.item, true);
            updateTodayTotal(todayTable.getData());
            expenseForm.reset();
            document.getElementById('id_quantity').value = 1;
            updateTotal();
        } catch (error) {
            console.error('Error adding expense:', error);
        }
    });

    editForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const id = document.getElementById('edit-id').value;
        const formData = new FormData(editForm);
        ['name', 'price', 'quantity', 'location', 'date', 'description'].forEach((field) => {
            formData.append(field, document.getElementById(`edit-${field}`).value);
        });

        try {
            const url = page.dataset.editUrlTemplate.replace('/0/', `/${id}/`);
            const data = await submitForm(url, formData);
            if (!data.success) {
                console.log(data.errors);
                return;
            }

            editingRow.update(data.item);
            updateTodayTotal(todayTable.getData());
            closeEditModal();
        } catch (error) {
            console.error('Error updating expense:', error);
        }
    });

    async function confirmDelete(row) {
        const item = row.getData();
        if (!confirm(`Are you sure you want to delete "${item.name}"?`)) return;

        const formData = new FormData();
        formData.append(
            'csrfmiddlewaretoken',
            document.querySelector('[name=csrfmiddlewaretoken]').value
        );

        try {
            const url = page.dataset.deleteUrlTemplate.replace('/0/', `/${item.id}/`);
            const data = await submitForm(url, formData);
            if (!data.success) {
                console.log(data.message);
                return;
            }

            await row.delete();
            updateTodayTotal(todayTable.getData());
        } catch (error) {
            console.error('Error deleting expense:', error);
        }
    }

    const todayTable = createTable();
    document.getElementById('id_price').addEventListener('input', updateTotal);
    document.getElementById('id_quantity').addEventListener('input', updateTotal);
    document.getElementById('edit-price').addEventListener('input', updateEditTotal);
    document.getElementById('edit-quantity').addEventListener('input', updateEditTotal);
    document.querySelectorAll('[data-close-edit]').forEach((button) => {
        button.addEventListener('click', closeEditModal);
    });
    updateTotal();
    updateTodayTotal(recentExpenses);
}());