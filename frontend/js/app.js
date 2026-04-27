// SmartPort Galicia - Frontend Application Script
// Real-time status monitoring and service integration

const API_BASE = '/api/v1';
const HEALTH_CHECK_INTERVAL = 10000; // 10 seconds

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartPort Frontend initialized');
    updateCurrentTime();
    checkSystemHealth();
    loadDashboardData();

    // Periodic health checks
    setInterval(checkSystemHealth, HEALTH_CHECK_INTERVAL);
    // Update time display
    setInterval(updateCurrentTime, 1000);
});

// ==================== Time Update ====================
function updateCurrentTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// ==================== System Health Check ====================
async function checkSystemHealth() {
    console.log('Checking system health...');

    // Check Backend
    checkService('backend', '/health', 'backend-status');

    // Check Orion-LD
    checkService('orion', '/ngsi-ld/v1/entities?limit=1', 'orion-status');

    // Check QuantumLeap
    checkService('quantumleap', '/v2/version', 'ql-status');

    // Check Grafana
    checkService('grafana', '/api/health', 'grafana-status');
}

async function checkService(name, endpoint, statusElementId) {
    try {
        const response = await fetch(endpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            setServiceStatus(statusElementId, 'success', 'En línea');
        } else {
            setServiceStatus(statusElementId, 'warning', 'Error');
        }
    } catch (error) {
        console.warn(`Service ${name} check failed:`, error);
        setServiceStatus(statusElementId, 'danger', 'Desconectado');
    }
}

function setServiceStatus(elementId, status, text) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Remove all status classes
    element.className = 'badge';

    // Add appropriate class
    switch (status) {
        case 'success':
            element.classList.add('bg-success');
            break;
        case 'warning':
            element.classList.add('bg-warning', 'text-dark');
            break;
        case 'danger':
            element.classList.add('bg-danger');
            break;
        default:
            element.classList.add('bg-secondary');
    }

    element.textContent = text;
}

// ==================== Dashboard Data Loading ====================
async function loadDashboardData() {
    console.log('Loading dashboard data...');

    try {
        // Load API data
        const response = await fetch(`${API_BASE}/`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log('API Response:', data);
            updateDashboard(data);
        }
    } catch (error) {
        console.warn('Error loading dashboard data:', error);
        loadMockData();
    }
}

function updateDashboard(data) {
    // Update dashboard with real data from API
    // For now, use mock data
    loadMockData();
}

// ==================== Mock Data (for demonstration) ====================
function loadMockData() {
    // KPIs
    document.getElementById('active-ports').textContent = '11';
    document.getElementById('available-berths').textContent = '23';
    document.getElementById('vessels-in-port').textContent = '8';
    document.getElementById('active-alerts').textContent = '2';

    // System status
    updateSystemStatus();

    // Load alerts
    loadAlerts();

    // Load operations
    loadOperations();
}

function updateSystemStatus() {
    const statuses = ['backend-status', 'orion-status', 'ql-status', 'grafana-status'];
    const allOnline = statuses.every(id => {
        const elem = document.getElementById(id);
        return elem && elem.classList.contains('bg-success');
    });

    const systemStatusBadge = document.getElementById('system-status');
    if (allOnline) {
        systemStatusBadge.className = 'badge bg-success';
        systemStatusBadge.textContent = 'Operativo';
    } else {
        systemStatusBadge.className = 'badge bg-warning text-dark';
        systemStatusBadge.textContent = 'Verificando...';
    }
}

function loadAlerts() {
    const alertsContainer = document.getElementById('alerts-container');

    const mockAlerts = [
        {
            id: 1,
            type: 'warning',
            title: 'Alta ocupación',
            message: 'Puerto de A Coruña: ocupación al 85%',
            time: '5 minutos atrás'
        },
        {
            id: 2,
            type: 'info',
            title: 'Atraque libre',
            message: 'Atraque A3 en Puerto de Vigo disponible',
            time: '15 minutos atrás'
        }
    ];

    alertsContainer.innerHTML = mockAlerts.map(alert => `
        <div class="alert alert-${alert.type} mb-3" role="alert">
            <strong>${alert.title}</strong>
            <p class="mb-1">${alert.message}</p>
            <small class="text-muted">${alert.time}</small>
        </div>
    `).join('');
}

function loadOperations() {
    const operationsContainer = document.getElementById('operations-table');

    const mockOperations = [
        {
            id: 'OP001',
            vessel: 'Aida Bella',
            port: 'A Coruña',
            berth: 'A1',
            operation: 'Carga',
            status: 'En progreso',
            progress: 65
        },
        {
            id: 'OP002',
            vessel: 'Ever Given',
            port: 'Vigo',
            berth: 'B2',
            operation: 'Descarga',
            status: 'En progreso',
            progress: 40
        },
        {
            id: 'OP003',
            vessel: 'Harmony',
            port: 'Ferrol',
            berth: 'C1',
            operation: 'Mantenimiento',
            status: 'Programado',
            progress: 0
        }
    ];

    operationsContainer.innerHTML = `
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Buque</th>
                    <th>Puerto</th>
                    <th>Atraque</th>
                    <th>Operación</th>
                    <th>Estado</th>
                    <th>Progreso</th>
                </tr>
            </thead>
            <tbody>
                ${mockOperations.map(op => `
                    <tr>
                        <td><small>${op.id}</small></td>
                        <td>${op.vessel}</td>
                        <td>${op.port}</td>
                        <td>${op.berth}</td>
                        <td>${op.operation}</td>
                        <td>
                            <span class="badge ${op.status === 'En progreso' ? 'bg-info' : 'bg-secondary'}">
                                ${op.status}
                            </span>
                        </td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${op.progress}%" 
                                     aria-valuenow="${op.progress}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                    ${op.progress}%
                                </div>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ==================== WebSocket Support (Future) ====================
// function setupWebSocket() {
//     const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
//     const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws`);
//
//     ws.onopen = () => console.log('WebSocket connected');
//     ws.onmessage = (event) => {
//         const data = JSON.parse(event.data);
//         console.log('WebSocket message:', data);
//         // Update UI with real-time data
//     };
//     ws.onerror = (error) => console.error('WebSocket error:', error);
//     ws.onclose = () => console.log('WebSocket disconnected');
// }

console.log('SmartPort Frontend app.js loaded');
