(function () {
    'use strict';

    const page = document.getElementById('record-list-page');
    const modal = document.getElementById('record-action-modal');
    const panel = modal.querySelector('.record-modal-panel');
    const title = document.getElementById('record-modal-title');
    const editPanel = modal.querySelector('[data-edit-panel]');
    const deletePanel = modal.querySelector('[data-delete-panel]');
    const editForm = document.getElementById('record-edit-form');
    const deleteForm = document.getElementById('record-delete-form');
    const editErrors = modal.querySelector('[data-edit-errors]');
    const dateInput = document.getElementById('record-date');
    let opener = null;

    function recordUrl(template, id) {
        return template.replace('/0/', `/${id}/`);
    }

    function openModal(trigger, mode) {
        opener = trigger;
        const label = page.dataset.recordLabel;
        const id = trigger.dataset.id;
        editPanel.hidden = mode !== 'edit';
        deletePanel.hidden = mode !== 'delete';

        if (mode === 'edit') {
            title.textContent = `Edit ${label}`;
            editForm.action = recordUrl(page.dataset.editUrlTemplate, id);
            document.getElementById('record-name').value = trigger.dataset.name;
            document.getElementById('record-amount').value = trigger.dataset.amount;
            dateInput.name = page.dataset.dateField;
            document.getElementById('record-date-label').textContent = `${label} Date`;
            dateInput.value = trigger.dataset.date;
            document.getElementById('record-return-date').value = trigger.dataset.returnDate;
            document.getElementById('record-description').value = trigger.dataset.description;
        } else {
            title.textContent = `Delete ${label}`;
            deleteForm.action = recordUrl(page.dataset.deleteUrlTemplate, id);
            document.getElementById('record-delete-name').textContent = trigger.dataset.name;
        }

        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        panel.focus();
    }

    function closeModal() {
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (opener) opener.focus();
        opener = null;
    }

    function showEditErrors(errors) {
        const messages = Object.values(errors || {}).flat().map((error) => error.message);
        editErrors.textContent = messages.join(' ')
            || 'Could not save changes. Please check the form and try again.';
        editErrors.hidden = false;
    }

    function updateEditedRow(record) {
        const row = opener.closest('tr');
        const cells = row.querySelectorAll('td');
        cells[1].textContent = record.name;
        cells[2].textContent = `৳${Number(record.amount).toFixed(2)}`;
        cells[3].textContent = record.date;
        cells[4].textContent = record.return_date || '-';
        cells[5].textContent = record.description || '-';

        Object.assign(opener.dataset, {
            name: record.name,
            amount: record.amount,
            date: record.date,
            returnDate: record.return_date,
            description: record.description
        });

        const total = [...page.querySelectorAll('.lend-table tbody tr')].reduce((sum, tableRow) => {
            return sum + (Number(tableRow.cells[2].textContent.replace(/[৳,\s]/g, '')) || 0);
        }, 0);
        page.querySelector('.lend-total').lastChild.textContent = `৳${total.toFixed(2)}`;
    }

    editForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        editErrors.hidden = true;

        try {
            const response = await fetch(editForm.action, {
                method: 'POST',
                body: new FormData(editForm),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                showEditErrors(data.errors);
                return;
            }

            updateEditedRow(data.record);
            closeModal();
        } catch (error) {
            showEditErrors({ request: [{ message: 'Could not save changes. Please try again.' }] });
        }
    });

    page.querySelectorAll('[data-edit-record]').forEach((button) => {
        button.addEventListener('click', () => openModal(button, 'edit'));
    });

    page.querySelectorAll('[data-delete-record]').forEach((button) => {
        button.addEventListener('click', () => openModal(button, 'delete'));
    });

    modal.querySelectorAll('[data-modal-close]').forEach((button) => {
        button.addEventListener('click', closeModal);
    });

    modal.addEventListener('click', (event) => {
        if (event.target === modal.querySelector('.record-modal-backdrop')) closeModal();
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.getAttribute('aria-hidden') === 'false') {
            closeModal();
        }
    });
}());