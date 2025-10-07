/**
 * Blood Request Management JavaScript
 * Handles all blood request-related functionality
 */

class RequestManager {
    constructor() {
        this.requests = [];
        this.filteredRequests = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadRequests();
    }

    bindEvents() {
        // Search and filter events
        document.getElementById('searchBtn').addEventListener('click', () => this.filterRequests());
        document.getElementById('searchPatient').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') this.filterRequests();
        });

        // Form submissions
        document.getElementById('addRequestForm').addEventListener('submit', (e) => this.handleAddRequest(e));
        document.getElementById('editRequestForm').addEventListener('submit', (e) => this.handleEditRequest(e));

        // Modal events
        document.getElementById('editFromDetailBtn').addEventListener('click', () => this.editFromDetail());
        document.getElementById('fulfillFromDetailBtn').addEventListener('click', () => this.fulfillFromDetail());

        // Real-time validation
        this.setupFormValidation();
    }

    setupFormValidation() {
        const addForm = document.getElementById('addRequestForm');
        const editForm = document.getElementById('editRequestForm');

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

    async loadRequests() {
        try {
            this.showLoading(true);
            this.requests = await API.get('/requests');
            this.filteredRequests = [...this.requests];
            this.renderRequests();
        } catch (error) {
            console.error('Error loading requests:', error);
            Utils.showAlert('Failed to load blood requests. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    filterRequests() {
        const searchPatient = document.getElementById('searchPatient').value.toLowerCase().trim();
        const filterBloodGroup = document.getElementById('filterBloodGroup').value;
        const filterUrgency = document.getElementById('filterUrgency').value;
        const filterStatus = document.getElementById('filterStatus').value;
        const filterCity = document.getElementById('filterCity').value.toLowerCase().trim();

        this.filteredRequests = this.requests.filter(request => {
            const matchesPatient = !searchPatient || request.patient_name.toLowerCase().includes(searchPatient);
            const matchesBloodGroup = !filterBloodGroup || request.blood_group === filterBloodGroup;
            const matchesUrgency = !filterUrgency || request.urgency === filterUrgency;
            const matchesStatus = !filterStatus || request.status === filterStatus;
            const matchesCity = !filterCity || request.city.toLowerCase().includes(filterCity);

            return matchesPatient && matchesBloodGroup && matchesUrgency && matchesStatus && matchesCity;
        });

        this.renderRequests();
    }

    renderRequests() {
        const tbody = document.getElementById('requestsTableBody');
        const emptyState = document.getElementById('emptyState');
        const tableContainer = document.getElementById('requestsTableContainer');
        const requestCount = document.getElementById('requestCount');

        // Update count
        requestCount.textContent = this.filteredRequests.length;

        if (this.filteredRequests.length === 0) {
            tableContainer.classList.add('d-none');
            emptyState.classList.remove('d-none');
            return;
        }

        tableContainer.classList.remove('d-none');
        emptyState.classList.add('d-none');

        tbody.innerHTML = this.filteredRequests.map(request => `
            <tr>
                <td>
                    <strong>${this.escapeHtml(request.patient_name)}</strong>
                </td>
                <td>
                    <span class="badge ${Utils.getBloodGroupClass(request.blood_group)} blood-group-badge">
                        ${request.blood_group}
                    </span>
                </td>
                <td>
                    <span class="${Utils.getUrgencyClass(request.urgency)}">
                        <i class="bi ${this.getUrgencyIcon(request.urgency)} me-1"></i>
                        ${request.urgency}
                    </span>
                </td>
                <td>${this.escapeHtml(request.city)}</td>
                <td>
                    ${request.hospital_name ? 
                        this.escapeHtml(request.hospital_name) : 
                        '<span class="text-muted">Not specified</span>'
                    }
                </td>
                <td>
                    <span class="badge ${request.status === 'Active' ? 'status-active' : 'status-fulfilled'}">
                        ${request.status}
                    </span>
                </td>
                <td>
                    <small class="text-muted">
                        ${Utils.formatDate(request.created_at)}
                    </small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary" onclick="requestManager.viewRequest(${request.id})" 
                                data-bs-toggle="tooltip" title="View Details">
                            <i class="bi bi-eye"></i>
                        </button>
                        ${request.status === 'Active' ? `
                            <button class="btn btn-outline-info" onclick="requestManager.findMatches(${request.id})"
                                    data-bs-toggle="tooltip" title="Find Donors">
                                <i class="bi bi-people"></i>
                            </button>
                            <button class="btn btn-outline-success" onclick="requestManager.fulfillRequest(${request.id})"
                                    data-bs-toggle="tooltip" title="Mark as Fulfilled">
                                <i class="bi bi-check-circle"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-outline-warning" onclick="requestManager.editRequest(${request.id})"
                                data-bs-toggle="tooltip" title="Edit Request">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="requestManager.deleteRequest(${request.id})"
                                data-bs-toggle="tooltip" title="Delete Request">
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

    getUrgencyIcon(urgency) {
        switch(urgency) {
            case 'Critical': return 'bi-exclamation-triangle-fill';
            case 'High': return 'bi-exclamation-circle-fill';
            case 'Medium': return 'bi-exclamation-circle';
            case 'Low': return 'bi-info-circle';
            default: return 'bi-circle';
        }
    }

    async handleAddRequest(e) {
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
            const requestData = Object.fromEntries(formData.entries());
            
            const newRequest = await API.post('/requests', requestData);
            
            // Add to local array
            this.requests.push(newRequest);
            this.filterRequests();
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addRequestModal'));
            modal.hide();
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            
            Utils.showAlert('Blood request created successfully!', 'success');
            
        } catch (error) {
            console.error('Error creating request:', error);
            Utils.showAlert('Failed to create blood request. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async handleEditRequest(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const requestId = document.getElementById('editRequestId').value;
        
        if (!Utils.validateForm(form)) {
            Utils.showAlert('Please fill in all required fields correctly.', 'warning');
            return;
        }

        try {
            Utils.showLoading(submitBtn);
            
            const formData = new FormData(form);
            const requestData = Object.fromEntries(formData.entries());
            delete requestData.id; // Remove id from data
            
            const updatedRequest = await API.put(`/requests/${requestId}`, requestData);
            
            // Update local array
            const index = this.requests.findIndex(r => r.id == requestId);
            if (index !== -1) {
                this.requests[index] = updatedRequest;
                this.filterRequests();
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editRequestModal'));
            modal.hide();
            
            Utils.showAlert('Blood request updated successfully!', 'success');
            
        } catch (error) {
            console.error('Error updating request:', error);
            Utils.showAlert('Failed to update blood request. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async viewRequest(requestId) {
        try {
            const request = await API.get(`/requests/${requestId}`);
            this.showRequestDetail(request);
        } catch (error) {
            console.error('Error loading request details:', error);
            Utils.showAlert('Failed to load request details.', 'danger');
        }
    }

    showRequestDetail(request) {
        const content = document.getElementById('requestDetailContent');
        content.innerHTML = `
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label text-muted">Patient Name</label>
                    <p class="fw-bold">${this.escapeHtml(request.patient_name)}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Blood Group Needed</label>
                    <p>
                        <span class="badge ${Utils.getBloodGroupClass(request.blood_group)} blood-group-badge">
                            ${request.blood_group}
                        </span>
                    </p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Urgency Level</label>
                    <p class="${Utils.getUrgencyClass(request.urgency)}">
                        <i class="bi ${this.getUrgencyIcon(request.urgency)} me-1"></i>
                        ${request.urgency}
                    </p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Status</label>
                    <p>
                        <span class="badge ${request.status === 'Active' ? 'status-active' : 'status-fulfilled'}">
                            ${request.status}
                        </span>
                    </p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">City</label>
                    <p class="fw-bold">${this.escapeHtml(request.city)}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label text-muted">Hospital</label>
                    <p>
                        ${request.hospital_name ? 
                            this.escapeHtml(request.hospital_name) : 
                            '<span class="text-muted">Not specified</span>'
                        }
                    </p>
                </div>
                <div class="col-12">
                    <label class="form-label text-muted">Contact Number</label>
                    <p>
                        <a href="tel:${request.contact_number}" class="text-decoration-none">
                            <i class="bi bi-telephone me-1"></i>${request.contact_number}
                        </a>
                    </p>
                </div>
                <div class="col-12">
                    <label class="form-label text-muted">Request Date</label>
                    <p class="text-muted">${Utils.formatDate(request.created_at)}</p>
                </div>
            </div>
        `;

        // Store request ID for buttons
        document.getElementById('editFromDetailBtn').setAttribute('data-request-id', request.id);
        document.getElementById('fulfillFromDetailBtn').setAttribute('data-request-id', request.id);

        // Show/hide fulfill button based on status
        const fulfillBtn = document.getElementById('fulfillFromDetailBtn');
        if (request.status === 'Active') {
            fulfillBtn.classList.remove('d-none');
        } else {
            fulfillBtn.classList.add('d-none');
        }

        const modal = new bootstrap.Modal(document.getElementById('requestDetailModal'));
        modal.show();
    }

    editRequest(requestId) {
        const request = this.requests.find(r => r.id == requestId);
        if (!request) return;

        // Populate edit form
        document.getElementById('editRequestId').value = request.id;
        document.getElementById('editPatientName').value = request.patient_name;
        document.getElementById('editRequestBloodGroup').value = request.blood_group;
        document.getElementById('editRequestCity').value = request.city;
        document.getElementById('editRequestUrgency').value = request.urgency;
        document.getElementById('editHospitalName').value = request.hospital_name || '';
        document.getElementById('editRequestContact').value = request.contact_number;

        const modal = new bootstrap.Modal(document.getElementById('editRequestModal'));
        modal.show();
    }

    editFromDetail() {
        const requestId = document.getElementById('editFromDetailBtn').getAttribute('data-request-id');
        
        // Close detail modal
        const detailModal = bootstrap.Modal.getInstance(document.getElementById('requestDetailModal'));
        detailModal.hide();
        
        // Open edit modal
        setTimeout(() => {
            this.editRequest(requestId);
        }, 300);
    }

    async fulfillRequest(requestId) {
        const request = this.requests.find(r => r.id == requestId);
        if (!request) return;

        if (!confirm(`Are you sure you want to mark the blood request for "${request.patient_name}" as fulfilled?`)) {
            return;
        }

        try {
            await API.post(`/requests/${requestId}/fulfill`);
            
            // Update local array
            const index = this.requests.findIndex(r => r.id == requestId);
            if (index !== -1) {
                this.requests[index].status = 'Fulfilled';
                this.filterRequests();
            }
            
            Utils.showAlert('Blood request marked as fulfilled successfully.', 'success');
            
        } catch (error) {
            console.error('Error fulfilling request:', error);
            Utils.showAlert('Failed to fulfill request. Please try again.', 'danger');
        }
    }

    fulfillFromDetail() {
        const requestId = document.getElementById('fulfillFromDetailBtn').getAttribute('data-request-id');
        
        // Close detail modal
        const detailModal = bootstrap.Modal.getInstance(document.getElementById('requestDetailModal'));
        detailModal.hide();
        
        // Fulfill request
        setTimeout(() => {
            this.fulfillRequest(requestId);
        }, 300);
    }

    async findMatches(requestId) {
        try {
            const matches = await API.get(`/requests/${requestId}/matches`);
            this.showDonorMatches(matches, requestId);
        } catch (error) {
            console.error('Error finding matches:', error);
            Utils.showAlert('Failed to find matching donors.', 'danger');
        }
    }

    showDonorMatches(matches, requestId) {
        const content = document.getElementById('donorMatchesContent');
        
        if (matches.length === 0) {
            content.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-people text-muted" style="font-size: 3rem;"></i>
                    <h4 class="mt-3 text-muted">No Matching Donors Found</h4>
                    <p class="text-muted">No donors found matching the blood group and city requirements.</p>
                </div>
            `;
        } else {
            content.innerHTML = `
                <div class="mb-3">
                    <h6 class="text-muted">Found ${matches.length} matching donor(s)</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Blood Group</th>
                                <th>City</th>
                                <th>Contact</th>
                                <th>Email</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${matches.map(donor => `
                                <tr>
                                    <td><strong>${this.escapeHtml(donor.name)}</strong></td>
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
                                            '<span class="text-muted">-</span>'
                                        }
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        const modal = new bootstrap.Modal(document.getElementById('donorMatchesModal'));
        modal.show();
    }

    async deleteRequest(requestId) {
        const request = this.requests.find(r => r.id == requestId);
        if (!request) return;

        if (!confirm(`Are you sure you want to delete the blood request for "${request.patient_name}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await API.delete(`/requests/${requestId}`);
            
            // Remove from local array
            this.requests = this.requests.filter(r => r.id != requestId);
            this.filterRequests();
            
            Utils.showAlert('Blood request deleted successfully.', 'success');
            
        } catch (error) {
            console.error('Error deleting request:', error);
            Utils.showAlert('Failed to delete blood request. Please try again.', 'danger');
        }
    }

    showLoading(show) {
        const spinner = document.querySelector('.loading-spinner');
        const tableContainer = document.getElementById('requestsTableContainer');
        
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

// Initialize request manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.requestManager = new RequestManager();
});