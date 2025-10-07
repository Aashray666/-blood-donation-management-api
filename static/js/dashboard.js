/**
 * Dashboard JavaScript
 * Handles dashboard functionality and statistics
 */

class Dashboard {
    constructor() {
        this.donors = [];
        this.requests = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDashboardData();
    }

    bindEvents() {
        // Quick add forms
        document.getElementById('quickAddDonorForm').addEventListener('submit', (e) => this.handleQuickAddDonor(e));
        document.getElementById('quickAddRequestForm').addEventListener('submit', (e) => this.handleQuickAddRequest(e));
    }

    async loadDashboardData() {
        try {
            // Load data in parallel
            const [donorsData, requestsData] = await Promise.all([
                API.get('/donors'),
                API.get('/requests')
            ]);

            this.donors = donorsData;
            this.requests = requestsData;

            // Update all dashboard components
            this.updateStatistics();
            this.renderRecentRequests();
            this.renderRecentDonors();
            this.renderBloodGroupDistribution();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            Utils.showAlert('Failed to load dashboard data. Please refresh the page.', 'danger');
        }
    }

    updateStatistics() {
        // Calculate statistics
        const totalDonors = this.donors.length;
        const activeRequests = this.requests.filter(r => r.status === 'Active').length;
        const fulfilledRequests = this.requests.filter(r => r.status === 'Fulfilled').length;
        const criticalRequests = this.requests.filter(r => r.urgency === 'Critical' && r.status === 'Active').length;

        // Update DOM elements
        document.getElementById('totalDonors').textContent = totalDonors;
        document.getElementById('activeRequests').textContent = activeRequests;
        document.getElementById('fulfilledRequests').textContent = fulfilledRequests;
        document.getElementById('criticalRequests').textContent = criticalRequests;

        // Add animation
        this.animateNumbers();
    }

    animateNumbers() {
        const numbers = document.querySelectorAll('.stats-number');
        numbers.forEach(number => {
            const target = parseInt(number.textContent);
            let current = 0;
            const increment = target / 20;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                number.textContent = Math.floor(current);
            }, 50);
        });
    }

    renderRecentRequests() {
        const tbody = document.getElementById('recentRequestsBody');
        const table = document.getElementById('recentRequestsTable');
        const loading = document.getElementById('requestsLoading');
        const emptyState = document.getElementById('noRequestsState');

        // Hide loading
        loading.classList.add('d-none');

        if (this.requests.length === 0) {
            emptyState.classList.remove('d-none');
            return;
        }

        // Show table
        table.classList.remove('d-none');

        // Get recent requests (last 5)
        const recentRequests = this.requests
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5);

        tbody.innerHTML = recentRequests.map(request => `
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
                    <span class="badge ${request.status === 'Active' ? 'status-active' : 'status-fulfilled'}">
                        ${request.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary btn-sm" onclick="dashboard.viewRequestDetails(${request.id})" 
                                data-bs-toggle="tooltip" title="View Details">
                            <i class="bi bi-eye"></i>
                        </button>
                        ${request.status === 'Active' ? `
                            <button class="btn btn-outline-info btn-sm" onclick="dashboard.findMatches(${request.id})"
                                    data-bs-toggle="tooltip" title="Find Donors">
                                <i class="bi bi-people"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(tbody.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    renderRecentDonors() {
        const tbody = document.getElementById('recentDonorsBody');
        const table = document.getElementById('recentDonorsTable');
        const loading = document.getElementById('donorsLoading');
        const emptyState = document.getElementById('noDonorsState');

        // Hide loading
        loading.classList.add('d-none');

        if (this.donors.length === 0) {
            emptyState.classList.remove('d-none');
            return;
        }

        // Show table
        table.classList.remove('d-none');

        // Get recent donors (last 5)
        const recentDonors = this.donors
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5);

        tbody.innerHTML = recentDonors.map(donor => `
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
                    <small class="text-muted">
                        ${Utils.formatDate(donor.created_at)}
                    </small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary btn-sm" onclick="dashboard.viewDonorDetails(${donor.id})" 
                                data-bs-toggle="tooltip" title="View Details">
                            <i class="bi bi-eye"></i>
                        </button>
                        <a href="/donors" class="btn btn-outline-warning btn-sm"
                           data-bs-toggle="tooltip" title="Manage Donors">
                            <i class="bi bi-pencil"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `).join('');

        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(tbody.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    renderBloodGroupDistribution() {
        const container = document.getElementById('bloodGroupList');
        const loading = document.getElementById('chartLoading');

        // Hide loading
        loading.classList.add('d-none');

        if (this.donors.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No donor data available</p>';
            container.classList.remove('d-none');
            return;
        }

        // Calculate blood group distribution
        const distribution = {};
        const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
        
        // Initialize all blood groups with 0
        bloodGroups.forEach(group => {
            distribution[group] = 0;
        });

        // Count donors by blood group
        this.donors.forEach(donor => {
            if (distribution.hasOwnProperty(donor.blood_group)) {
                distribution[donor.blood_group]++;
            }
        });

        // Calculate percentages
        const total = this.donors.length;
        
        container.innerHTML = bloodGroups.map(group => {
            const count = distribution[group];
            const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
            
            return `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div class="d-flex align-items-center">
                        <span class="badge ${Utils.getBloodGroupClass(group)} blood-group-badge me-2">
                            ${group}
                        </span>
                        <span class="text-muted">${count} donors</span>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div class="progress-bar bg-danger" role="progressbar" 
                                 style="width: ${percentage}%" aria-valuenow="${percentage}" 
                                 aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <small class="text-muted">${percentage}%</small>
                    </div>
                </div>
            `;
        }).join('');

        container.classList.remove('d-none');
    }

    async handleQuickAddDonor(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!Utils.validateForm(form)) {
            Utils.showAlert('Please fill in all required fields.', 'warning');
            return;
        }

        try {
            Utils.showLoading(submitBtn);
            
            const formData = new FormData(form);
            const donorData = Object.fromEntries(formData.entries());
            
            const newDonor = await API.post('/donors', donorData);
            
            // Add to local array and refresh dashboard
            this.donors.push(newDonor);
            this.updateStatistics();
            this.renderRecentDonors();
            this.renderBloodGroupDistribution();
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('quickAddDonorModal'));
            modal.hide();
            form.reset();
            
            Utils.showAlert('Donor added successfully!', 'success');
            
        } catch (error) {
            console.error('Error adding donor:', error);
            Utils.showAlert('Failed to add donor. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async handleQuickAddRequest(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!Utils.validateForm(form)) {
            Utils.showAlert('Please fill in all required fields.', 'warning');
            return;
        }

        try {
            Utils.showLoading(submitBtn);
            
            const formData = new FormData(form);
            const requestData = Object.fromEntries(formData.entries());
            
            const newRequest = await API.post('/requests', requestData);
            
            // Add to local array and refresh dashboard
            this.requests.push(newRequest);
            this.updateStatistics();
            this.renderRecentRequests();
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('quickAddRequestModal'));
            modal.hide();
            form.reset();
            
            Utils.showAlert('Blood request created successfully!', 'success');
            
        } catch (error) {
            console.error('Error creating request:', error);
            Utils.showAlert('Failed to create blood request. Please try again.', 'danger');
        } finally {
            Utils.hideLoading(submitBtn);
        }
    }

    async viewDonorDetails(donorId) {
        try {
            const donor = await API.get(`/donors/${donorId}`);
            
            Utils.showAlert(`
                <strong>Donor Details:</strong><br>
                <strong>Name:</strong> ${this.escapeHtml(donor.name)}<br>
                <strong>Blood Group:</strong> ${donor.blood_group}<br>
                <strong>City:</strong> ${this.escapeHtml(donor.city)}<br>
                <strong>Contact:</strong> ${donor.contact_number}
            `, 'info');
            
        } catch (error) {
            console.error('Error loading donor details:', error);
            Utils.showAlert('Failed to load donor details.', 'danger');
        }
    }

    async viewRequestDetails(requestId) {
        try {
            const request = await API.get(`/requests/${requestId}`);
            
            Utils.showAlert(`
                <strong>Request Details:</strong><br>
                <strong>Patient:</strong> ${this.escapeHtml(request.patient_name)}<br>
                <strong>Blood Group:</strong> ${request.blood_group}<br>
                <strong>Urgency:</strong> ${request.urgency}<br>
                <strong>City:</strong> ${this.escapeHtml(request.city)}<br>
                <strong>Status:</strong> ${request.status}
            `, 'info');
            
        } catch (error) {
            console.error('Error loading request details:', error);
            Utils.showAlert('Failed to load request details.', 'danger');
        }
    }

    async findMatches(requestId) {
        try {
            const matches = await API.get(`/requests/${requestId}/matches`);
            
            if (matches.length === 0) {
                Utils.showAlert('No matching donors found for this request.', 'warning');
            } else {
                Utils.showAlert(`Found ${matches.length} matching donor(s). <a href="/requests" class="alert-link">View details</a>`, 'success');
            }
            
        } catch (error) {
            console.error('Error finding matches:', error);
            Utils.showAlert('Failed to find matching donors.', 'danger');
        }
    }

    searchDonors() {
        // Redirect to donors page with search functionality
        window.location.href = '/donors';
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});