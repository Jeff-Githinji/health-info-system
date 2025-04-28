class HealthSystem {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.initEventListeners();
        this.loadInitialData();
    }

    initEventListeners() {
        document.getElementById('programForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleProgramCreate();
        });

        document.getElementById('clientForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleClientCreate();
        });

        document.getElementById('searchInput')?.addEventListener('input', 
            this.debounce(() => this.handleClientSearch(), 300)
        );
    }

    async loadInitialData() {
        try {
            this.toggleLoading(true);
            const [programs, clients] = await Promise.all([
                this.fetchData('/programs'),
                this.fetchData('/clients')
            ]);
            this.renderPrograms(programs);
            this.renderClients(clients);
        } catch (error) {
            this.showMessage('error', error.message);
        } finally {
            this.toggleLoading(false);
        }
    }

    async fetchData(endpoint, method = 'GET', body = null) {
        try {
            const response = await fetch(`${this.apiBase}${endpoint}`, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': 'your-secret-key-123'
                },
                body: body ? JSON.stringify(body) : null
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    // Program Methods
    async handleProgramCreate() {
        const programName = document.getElementById('programName').value;
        const button = document.querySelector('#programForm button');
        
        try {
            this.toggleButtonLoading(button, true);
            const newProgram = await this.fetchData('/programs', 'POST', { name: programName });
            this.loadInitialData();
            this.showMessage('success', `Program "${newProgram.name}" created!`, 'programMessage');
            document.getElementById('programForm').reset();
        } catch (error) {
            this.handleProgramError(error, 'programMessage');
        } finally {
            this.toggleButtonLoading(button, false);
        }
    }

    async deleteProgram(programId) {
        if (!confirm('Are you sure you want to delete this program?')) return;
        
        try {
            await this.fetchData(`/programs/${programId}`, 'DELETE');
            this.loadInitialData();
            this.showMessage('success', 'Program deleted successfully');
        } catch (error) {
            this.showMessage('error', 'Failed to delete program');
            console.error('Delete error:', error);
        }
    }

    renderPrograms(programs) {
        const container = document.getElementById('programsList');
        if (!container) return;
        
        container.innerHTML = programs.map(program => `
            <div class="d-flex align-items-center mb-2">
                <div class="custom-control custom-checkbox flex-grow-1">
                    <input type="checkbox" class="custom-control-input" 
                        id="program-${program.id}" value="${program.id}">
                    <label class="custom-control-label" for="program-${program.id}">
                        ${program.name}
                    </label>
                </div>
                <button class="btn btn-sm btn-danger ml-2" 
                    onclick="healthSystem.deleteProgram(${program.id})">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        `).join('');
    }

    // Client Methods
    async handleClientCreate() {
        const clientData = {
            name: document.getElementById('clientName').value,
            email: document.getElementById('clientEmail').value,
            programs: Array.from(document.querySelectorAll('#programsList input:checked'))
                         .map(input => parseInt(input.value))
        };
        const button = document.querySelector('#clientForm button');

        try {
            this.toggleButtonLoading(button, true);
            const newClient = await this.fetchData('/clients', 'POST', clientData);
            this.loadInitialData();
            this.showMessage('success', 'Client created!', 'clientMessage');
            document.getElementById('clientForm').reset();
        } catch (error) {
            this.handleClientError(error, 'clientMessage');
        } finally {
            this.toggleButtonLoading(button, false);
        }
    }

    async deleteClient(clientId) {
        if (!confirm('Are you sure you want to delete this client?')) return;
        
        try {
            await this.fetchData(`/clients/${clientId}`, 'DELETE');
            this.loadInitialData();
            this.showMessage('success', 'Client deleted successfully');
        } catch (error) {
            this.showMessage('error', 'Failed to delete client');
            console.error('Delete error:', error);
        }
    }

    renderClients(clients) {
        const tbody = document.getElementById('clientTable');
        if (!tbody) return;
        
        if (clients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted py-4">
                        No clients have been registered yet
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = clients.map(client => `
            <tr>
                <td>${client.name}</td>
                <td>${client.email}</td>
                <td>${client.programs.map(p => p.name).join(', ') || 'None'}</td>
                <td>
                    <button class="btn btn-sm btn-danger" 
                        onclick="healthSystem.deleteClient(${client.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // Search Functionality
    debounce(func, timeout = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => { func.apply(this, args); }, timeout);
        };
    }

    async handleClientSearch() {
        const query = document.getElementById('searchInput').value;
        try {
            this.toggleLoading(true);
            const results = await this.fetchData(`/clients/search?query=${encodeURIComponent(query)}`);
            this.renderClients(results);
        } catch (error) {
            this.showMessage('error', error.message);
        } finally {
            this.toggleLoading(false);
        }
    }

    // Utility Methods
    toggleLoading(show) {
        const loader = document.getElementById('loadingOverlay');
        if (loader) loader.style.display = show ? 'flex' : 'none';
    }

    toggleButtonLoading(button, show) {
        if (!button) return;
        button.disabled = show;
        
        const submitText = button.querySelector('.submit-text');
        const spinner = button.querySelector('.spinner-border');
        
        if (submitText) submitText.classList.toggle('d-none', show);
        if (spinner) spinner.classList.toggle('d-none', !show);
    }

    showMessage(type, text, containerId = 'globalMessage') {
        const colors = {
            success: 'alert-success',
            error: 'alert-danger',
            info: 'alert-info'
        };
        
        const messageDiv = document.getElementById(containerId);
        if (!messageDiv) return;
        
        messageDiv.innerHTML = `
            <div class="alert ${colors[type]} alert-dismissible fade show">
                ${text}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `;
    }

    handleProgramError(error, containerId) {
        if (error.message.includes('409')) {
            this.showMessage('error', 'Program already exists!', containerId);
        } else if (error.message.includes('400')) {
            this.showMessage('error', 'Program name required!', containerId);
        } else {
            this.showMessage('error', error.message, containerId);
        }
    }

    handleClientError(error, containerId) {
        if (error.message.includes('409')) {
            this.showMessage('error', 'Email already exists!', containerId);
        } else if (error.message.includes('400')) {
            this.showMessage('error', 'Name and email required!', containerId);
        } else {
            this.showMessage('error', error.message, containerId);
        }
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    window.healthSystem = new HealthSystem();
});