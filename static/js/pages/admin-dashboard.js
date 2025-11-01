/**
 * Admin Dashboard Page Module
 * Lógica específica del panel de administración
 */

import { TableSearch } from '../components/search.js';
import { chartManager } from '../components/charts.js';
import { DOM } from '../utils/dom.js';
import { Animations } from '../utils/animations.js';

export class AdminDashboardPage {
  constructor() {
    this.init();
  }

  init() {
    this.setupSearches();
    this.setupCharts();
    this.setupHoverEffects();
    this.setupStatsAnimation();
  }

  /**
   * Configura las búsquedas de las tablas
   */
  setupSearches() {
    new TableSearch('course-search-input', 'course-table');
    new TableSearch('user-search-input', 'user-table');
    new TableSearch('access-search-input', 'access-table');
  }

  /**
   * Configura los gráficos del dashboard
   */
  setupCharts() {
    // Net Sales Chart
    const ventasNetasCanvas = DOM.$('#ventasNetasChart');
    if (ventasNetasCanvas) {
      // Obtener datos del template (inyectados por Jinja)
      const ventasData = window.ventasNetasData || {
        dia: 0,
        semana: 0,
        mes: 0,
        ano: 0
      };

      chartManager.createBarChart('ventasNetasChart', {
        labels: ['Hoy', 'Semana', 'Mes', 'Año'],
        data: [
          ventasData.dia,
          ventasData.semana,
          ventasData.mes,
          ventasData.ano
        ],
        label: 'Ventas Netas (USD)',
        colors: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(251, 146, 60, 0.8)'
        ],
        borderColors: [
          'rgba(99, 102, 241, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(236, 72, 153, 1)',
          'rgba(251, 146, 60, 1)'
        ],
        yTicks: {
          callback: function(value) {
            return '$' + value;
          }
        }
      });
    }
  }

  /**
   * Configura efectos hover en cards
   */
  setupHoverEffects() {
    const cards = DOM.$$('.card, .gradient-card');

    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
      });

      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
      });
    });
  }

  /**
   * Anima estadísticas al hacer scroll
   */
  setupStatsAnimation() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const target = entry.target;
          const valueText = target.textContent.replace(/[^\d]/g, '');
          const value = parseInt(valueText);

          if (value > 0) {
            Animations.animateCurrency(target, 0, value, 1000);
          }

          observer.unobserve(target);
        }
      });
    });

    // Observar valores estadísticos
    DOM.$$('.text-2xl.font-bold').forEach(el => {
      if (el.textContent.includes('$')) {
        observer.observe(el);
      }
    });
  }
}

// Auto-inicialización
DOM.ready(() => {
  if (document.body.classList.contains('page-admin-dashboard') ||
      window.location.pathname.includes('admin_dashboard')) {
    new AdminDashboardPage();
  }
});
