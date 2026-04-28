/**
 * Chart Components with Chart.js
 */

export class ChartController {
  constructor(canvasId, type = 'line', options = {}) {
    this.canvasId = canvasId;
    this.type = type;
    this.chart = null;
    this.options = options;
    this.defaultOptions = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: options.title || 'Chart',
        },
      },
    };
  }

  init(data, chartOptions = {}) {
    const canvas = document.getElementById(this.canvasId);
    if (!canvas) {
      console.error(`Canvas ${this.canvasId} not found`);
      return false;
    }

    const ctx = canvas.getContext('2d');

    const finalOptions = {
      ...this.defaultOptions,
      ...chartOptions,
    };

    try {
      this.chart = new Chart(ctx, {
        type: this.type,
        data: data,
        options: finalOptions,
      });
      return true;
    } catch (error) {
      console.error('Failed to initialize chart:', error);
      return false;
    }
  }

  update(data) {
    if (this.chart) {
      this.chart.data = data;
      this.chart.update();
    }
  }

  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }
}

/**
 * Berth Occupancy Status Chart
 */

export function BerthOccupancyChart(
  { free = 0, occupied = 0, reserved = 0, unavailable = 0 },
  canvasId = 'berth-occupancy-chart'
) {
  return {
    canvas: `<canvas id="${canvasId}"></canvas>`,
    data: {
      labels: ['Libre', 'Ocupado', 'Reservado', 'No disponible'],
      datasets: [
        {
          label: 'Atraques',
          data: [free, occupied, reserved, unavailable],
          backgroundColor: [
            '#28a745',
            '#dc3545',
            '#ffc107',
            '#6c757d',
          ],
          borderColor: [
            '#1e7e34',
            '#bb2d3b',
            '#e0a800',
            '#545b62',
          ],
          borderWidth: 2,
        },
      ],
    },
    options: {
      type: 'doughnut',
      title: 'Ocupación de Atraques',
    },
  };
}

/**
 * Alert Severity Distribution Chart
 */

export function AlertSeverityChart(
  { high = 0, medium = 0, low = 0 },
  canvasId = 'alert-severity-chart'
) {
  return {
    canvas: `<canvas id="${canvasId}"></canvas>`,
    data: {
      labels: ['Alta', 'Media', 'Baja'],
      datasets: [
        {
          label: 'Alertas',
          data: [high, medium, low],
          backgroundColor: [
            '#dc3545',
            '#fd7e14',
            '#17a2b8',
          ],
          borderColor: [
            '#bb2d3b',
            '#dc6311',
            '#0c5460',
          ],
          borderWidth: 2,
        },
      ],
    },
    options: {
      type: 'bar',
      title: 'Alertas por Severidad',
    },
  };
}

/**
 * Port Call Timeline Chart
 */

export function PortCallTimelineChart(portCalls = [], canvasId = 'portcall-timeline-chart') {
  const hours = {};

  // Group portcalls by hour
  portCalls.forEach((pc) => {
    const date = new Date(pc.eta);
    const hour = `${date.getHours()}:00`;
    hours[hour] = (hours[hour] || 0) + 1;
  });

  const labels = Object.keys(hours).sort();
  const data = labels.map((h) => hours[h]);

  return {
    canvas: `<canvas id="${canvasId}"></canvas>`,
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Escalas Previstas',
          data: data,
          backgroundColor: '#007bff',
          borderColor: '#0056b3',
          borderWidth: 2,
          tension: 0.1,
        },
      ],
    },
    options: {
      type: 'line',
      title: 'Escalas Previstas (Próximas 24h)',
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  };
}

/**
 * Occupancy Trend Chart
 */

export function OccupancyTrendChart(
  timeSeriesData = [],
  canvasId = 'occupancy-trend-chart'
) {
  const labels = timeSeriesData.map((d) => new Date(d.timestamp).toLocaleTimeString());
  const data = timeSeriesData.map((d) => d.occupancy_percent);

  return {
    canvas: `<canvas id="${canvasId}"></canvas>`,
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Ocupación %',
          data: data,
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          borderWidth: 2,
          tension: 0.1,
          fill: true,
        },
      ],
    },
    options: {
      type: 'line',
      title: 'Tendencia de Ocupación',
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
        },
      },
    },
  };
}

/**
 * Availability by Facility Chart
 */

export function AvailabilityByFacilityChart(
  facilities = {},
  canvasId = 'availability-facility-chart'
) {
  const labels = Object.keys(facilities);
  const freeData = labels.map((f) => facilities[f].free || 0);
  const occupiedData = labels.map((f) => facilities[f].occupied || 0);
  const reservedData = labels.map((f) => facilities[f].reserved || 0);

  return {
    canvas: `<canvas id="${canvasId}"></canvas>`,
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Libre',
          data: freeData,
          backgroundColor: '#28a745',
        },
        {
          label: 'Ocupado',
          data: occupiedData,
          backgroundColor: '#dc3545',
        },
        {
          label: 'Reservado',
          data: reservedData,
          backgroundColor: '#ffc107',
        },
      ],
    },
    options: {
      type: 'bar',
      title: 'Disponibilidad por Facility',
      scales: {
        x: {
          stacked: false,
        },
        y: {
          stacked: false,
        },
      },
    },
  };
}

/**
 * Chart Container Component
 */

export function ChartContainer({
  chartId = 'chart-default',
  title = 'Chart',
  width = '100%',
  height = '300px',
}) {
  return `
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">${title}</h6>
      </div>
      <div class="card-body">
        <canvas id="${chartId}" style="max-height: ${height};"></canvas>
      </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
  `;
}
