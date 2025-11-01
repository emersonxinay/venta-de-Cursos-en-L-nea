/**
 * Charts Component
 * Wrapper para Chart.js con configuraciones predefinidas
 */

export class ChartManager {
  constructor() {
    this.charts = {};
    this.defaultColors = {
      primary: 'rgba(99, 102, 241, 0.8)',
      secondary: 'rgba(139, 92, 246, 0.8)',
      success: 'rgba(34, 197, 94, 0.8)',
      warning: 'rgba(251, 146, 60, 0.8)',
      danger: 'rgba(239, 68, 68, 0.8)',
      info: 'rgba(59, 130, 246, 0.8)'
    };
  }

  /**
   * Crea un gradiente
   */
  createGradient(ctx, color1, color2, height = 400) {
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
  }

  /**
   * Crea un gráfico de barras
   */
  createBarChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas not found: ${canvasId}`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    const data = {
      labels: config.labels || [],
      datasets: [{
        label: config.label || 'Data',
        data: config.data || [],
        backgroundColor: config.colors || [
          this.defaultColors.primary,
          this.defaultColors.secondary,
          this.defaultColors.warning,
          this.defaultColors.success
        ],
        borderColor: config.borderColors || config.colors || [
          'rgba(99, 102, 241, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(251, 146, 60, 1)',
          'rgba(34, 197, 94, 1)'
        ],
        borderWidth: config.borderWidth || 2,
        borderRadius: config.borderRadius || 8
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: config.showLegend !== undefined ? config.showLegend : false
        },
        tooltip: {
          callbacks: config.tooltipCallbacks || {}
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: config.yTicks || {}
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    };

    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: options
    });

    return this.charts[canvasId];
  }

  /**
   * Crea un gráfico de línea
   */
  createLineChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas not found: ${canvasId}`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    const gradient = this.createGradient(
      ctx,
      config.gradientStart || 'rgba(99, 102, 241, 0.4)',
      config.gradientEnd || 'rgba(99, 102, 241, 0.0)'
    );

    const data = {
      labels: config.labels || [],
      datasets: [{
        label: config.label || 'Data',
        data: config.data || [],
        backgroundColor: gradient,
        borderColor: config.borderColor || this.defaultColors.primary,
        borderWidth: config.borderWidth || 2,
        fill: config.fill !== undefined ? config.fill : true,
        tension: config.tension || 0.4
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: config.showLegend !== undefined ? config.showLegend : false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    };

    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    });

    return this.charts[canvasId];
  }

  /**
   * Crea un gráfico de dona/pie
   */
  createDoughnutChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas not found: ${canvasId}`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    const data = {
      labels: config.labels || [],
      datasets: [{
        data: config.data || [],
        backgroundColor: config.colors || Object.values(this.defaultColors),
        borderWidth: config.borderWidth || 0
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: config.showLegend !== undefined ? config.showLegend : true,
          position: config.legendPosition || 'bottom'
        }
      }
    };

    this.charts[canvasId] = new Chart(ctx, {
      type: config.type || 'doughnut',
      data: data,
      options: options
    });

    return this.charts[canvasId];
  }

  /**
   * Actualiza datos de un gráfico
   */
  updateChart(canvasId, newData) {
    const chart = this.charts[canvasId];
    if (!chart) {
      console.error(`Chart not found: ${canvasId}`);
      return;
    }

    chart.data.datasets[0].data = newData;
    chart.update();
  }

  /**
   * Destruye un gráfico
   */
  destroyChart(canvasId) {
    const chart = this.charts[canvasId];
    if (chart) {
      chart.destroy();
      delete this.charts[canvasId];
    }
  }

  /**
   * Destruye todos los gráficos
   */
  destroyAll() {
    Object.keys(this.charts).forEach(id => this.destroyChart(id));
  }
}

// Instancia global
export const chartManager = new ChartManager();
