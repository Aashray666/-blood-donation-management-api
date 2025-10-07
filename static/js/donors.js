/**
 * Donor Management JavaScript
 * Handles all donor-related functionality
 */

class DonorManager {
    constructor() {
        this.donors = [];
        this.filteredDonors = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDonors();
    }

    bindEvents() {
        // Search and filter events
        document.getElementById('searchBtn').addEventListener('click', () => this.filterDonors());
        document.getElementById('searchName').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') this.filterDonors();
        });

        // Form submissions
        document.getElementById('addDonorForm').addEventListener('submit', (e) => this.handleAddDonor(e));
        document.getElementById('editDonorForm').addEventListener('submit', (e) => this.handleEditDonor(e));

        // Modal events
        document.getElementById('editFromDetailBtn').addEventListener('click', () => this.editFromDetail());

        // Real-time validation
        this.setupFormValidation();
    }

    setupFormValidation() {
        // Add donor form validation
        const addForm = document.getElementById('addDonorForm');
        const editForm = document.getElementById('editDonorForm');

        [addForm, editForm].forEach(form => {
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldError(input));
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
        }

        // Email validation
        if (field.type === 'email' && value && !Utils.validateEmail(value)) {
            isValid = false;
        }

        // Phone validation
        if (field.type === 'tel' && value && !Utils.validatePhone(value)) {
            isValid = false;
        }

        // Update field appearance
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }

        return isValid;
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        if (field.value.trim()) {
            field.classList.remove('is-valid');
        }
    }

    async loadDonors() {
        try {
            this.showLoading(true);
            this.donors = await API.get('/donors');
            this.filteredDonors = [...this.donors];
            this.renderDonors();
        } catch (error) {
            console.error('Error loading donors:', error);
            Utils.showAlert('Failed to load donors. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    filterDonors() {
        const searchName = document.getElementById('searchName').value.toLowerCase().trim();
        const filterBloodGroup = document.getElementById('filterBloodGroup').value;
        const filterCity = document.getElementById('filterCity').value.toLowerCase().trim();

        this.filteredDonors = this.donors.filter(donor => {
            const matchesName = !searchName || donor.name.toLowerCase().includes(searchName);
            const matchesBloodGroup = !filterBloodGroup || donor.blood_group === filterBloodGroup;
            const matchesCity = !filterCity || donor.city.toLowerCase().includes(filterCity);

            return matchesName && matchesBloodGroup && matchesCity;
        });

        this.renderDonors();
    }

    renderDonors() {
        const tbody = document.getElementById('donorsTableBody');
        const emptyState = document.getElementById('emptyState');
        const tableContainer = document.getElementById('donorsTableContainer');
        const donorCount = document.getElementById('donorCount');

        // Update count
        donorCount.textContent = this.filteredDonors.length;

        if (this.filteredDonors.length === 0) {
            tableContainer.classList.add('d-none');
            emptyState.classList.remove('d-none');
            return;
        }

        tableContainer.classList.remove('d-none');
        emptyState.classList.add('d-none');

        tbody.innerHTML = this.filteredDonors.map(donor => `
            <tr>
                <td>
                    <strong>${this.escapeHtml(donor.name)}</strong>
                </td>
                <td>
                    <span class="badge ${Utils.getBloodGroupClass(donor.blood_group)} blood-group-badge">
                        ${donor.blood_group}
                    </span>
                </td>
                <td>${this.escapeHtml(donor.city)}</td>
                <td>
                    <a href="tel:${donor.contact_number}" class="text-decoration-none">
                        <i class="bi bi-telephone me-1"></i>${donor.contact_number}
                    </a>
                </td>
                <td>
                    ${donor.email ? 
                        `<a href="mailto:${donor.email}" class="text-decoration-none">
                            <i class="bi bi-envelope me-1"></i>${this.escapeHtml(donor.email)}
                        </a>` : 
                        '<span class="text-muted">Not provided</span>'
                    }
                </td>
                <td>
                    <small class="text-muted">
                        ${Utils.formatDate(donor.created_at)}
                    </small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary" onclick="donorManager.viewDonor(${donor.id})" 
                                data-bs-toggle="tooltip" title="View Details">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-outline-warning" onclick="donorManager.editDonor(${donor.id})"
                                data-bs-toggle="tooltip" title="Edit Donor">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="donorManager.deleteDonor(${donor.id})"
                                data-bs-toggle="tooltip" title="Delete Donor">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        // Reinitialize tooltips
        const tooltipTriggerList = [].slice.call(tbody.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    async handleAddDonor(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!Utils.validateForm(form)) {
            Utils.showAlert('Please fill in all required fields correctly.', 'warning');
            return;
        }

        try {
            Utils.showLoading(submitBtn);
            
            const formData = new FormData(form);
            const donorData = Object.fromEntries(formData.entries());
            
            const newDonor = await API.post('/donors', donorData);
            
            // Add to local array
            this.donors.push(newDonor);
            this.filterDonors();
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addDonorModal'));
            modal.hide();
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            
            Utils.showAlert('Donor added successfully!', 'success');
            
        } catch (error) {
            console.error('Error adding donor:', error);
            Utils.showAlert('Failed to add donor. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async handleEditDonor(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const donorId = document.getElementById('editDonorId').value;
        
        if (!Utils.validateForm(form)) {
            Utils.showAlert('Please fill in all required fields correctly.', 'warning');
            return;
        }

        try {
            Utils.showLoading(submitBtn);
            
            const formData = new FormData(form);
            const donorData = Object.fromEntries(formData.entries());
            delete donorData.id; // Remove id from data
            
            const updatedDonor = await API.put(`/donors/${donorId}`, donorData);
            
            // Update local array
            const index = this.donors.findIndex(d => d.id == donorId);
            if (index !== -1) {
                this.donors[index] = updatedDonor;
                this.filterDonors();
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editDonorModal'));
            modal.hide();
            
            Utils.showAlert('Donor updated successfully!', 'success');
            
        } catch (error) {
            console.error('Error updating donor:', error);
            Utils.showAlert('Failed to update donor. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async viewDonor(donorId) {
        try {
            const donor = await API.get(`/donors/${donorId}`);
            this.showDonorDetail(donor);
        } catch (error) {
            console.error('Error loading donor details:', error);
            Utils.showAlert('Failed to load donor details.', 'danger');
        }
    }

    showDonorDetail(donor) {
        const content = document.getElementById('donorDetailContent');
        content.innerHTML = `
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label text-muted">Full Name</label>
                    <p class="fw-bold">${this.escapeHtml(donor.name)}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Blood Group</label>
                    <p>
                        <span class="badge ${Utils.getBloodGroupClass(donor.blood_group)} blood-group-badge">
                            ${donor.blood_group}
                        </span>
                    </p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">City</label>
                    <p class="fw-bold">${this.escapeHtml(donor.city)}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Contact Number</label>
                    <p>
                        <a href="tel:${donor.contact_number}" class="text-decoration-none">
                            <i class="bi bi-telephone me-1"></i>${donor.contact_number}
                        </a>
                    </p>
                </div>
                <div class="col-12">
                    <label class="form-label text-muted">Email Address</label>
                    <p>
                        ${donor.email ? 
                            `<a href="mailto:${donor.email}" class="text-decoration-none">
                                <i class="bi bi-envelope me-1"></i>${this.escapeHtml(donor.email)}
                            </a>` : 
                            '<span class="text-muted">Not provided</span>'
                        }
                    </p>
                </div>
                <div class="col-12">
                    <label class="form-label text-muted">Registration Date</label>
                    <p class="text-muted">${Utils.formatDate(donor.created_at)}</p>
                </div>
            </div>
        `;

        // Store donor ID for edit button
        document.getElementById('editFromDetailBtn').setAttribute('data-donor-id', donor.id);

        const modal = new bootstrap.Modal(document.getElementById('donorDetailModal'));
        modal.show();
    }

    editDonor(donorId) {
        const donor = this.donors.find(d => d.id == donorId);
        if (!donor) return;

        // Populate edit form
        document.getElementById('editDonorId').value = donor.id;
        document.getElementById('editDonorName').value = donor.name;
        document.getElementById('editDonorBloodGroup').value = donor.blood_group;
        document.getElementById('editDonorCity').value = donor.city;
        document.getElementById('editDonorContact').value = donor.contact_number;
        document.getElementById('editDonorEmail').value = donor.email || '';

        const modal = new bootstrap.Modal(document.getElementById('editDonorModal'));
        modal.show();
    }

    editFromDetail() {
        const donorId = document.getElementById('editFromDetailBtn').getAttribute('data-donor-id');
        
        // Close detail modal
        const detailModal = bootstrap.Modal.getInstance(document.getElementById('donorDetailModal'));
        detailModal.hide();
        
        // Open edit modal
        setTimeout(() => {
            this.editDonor(donorId);
        }, 300);
    }

    async deleteDonor(donorId) {
        const donor = this.donors.find(d => d.id == donorId);
        if (!donor) return;

        if (!confirm(`Are you sure you want to delete donor "${donor.name}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await API.delete(`/donors/${donorId}`);
            
            // Remove from local array
            this.donors = this.donors.filter(d => d.id != donorId);
            this.filterDonors();
            
            Utils.showAlert('Donor deleted successfully.', 'success');
            
        } catch (error) {
            console.error('Error deleting donor:', error);
            Utils.showAlert('Failed to delete donor. Please try again.', 'danger');
        }
    }

    showLoading(show) {
        const spinner = document.querySelector('.loading-spinner');
        const tableContainer = document.getElementById('donorsTableContainer');
        
        if (show) {
            spinner.style.display = 'block';
            tableContainer.style.display = 'none';
        } else {
            spinner.style.display = 'none';
            tableContainer.style.display = 'block';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize donor manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.donorManager = new DonorManager();
});