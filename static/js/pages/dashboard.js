/**
 * Dashboard Page Module
 * Lógica específica de la página de dashboard
 */

import { Search } from '../components/search.js';
import { DOM } from '../utils/dom.js';

export class DashboardPage {
  constructor() {
    this.searchInput = null;
    this.sortSelect = null;
    this.courseItems = [];

    this.init();
  }

  init() {
    this.setupSearch();
    this.setupSort();
  }

  /**
   * Configura la búsqueda de cursos
   */
  setupSearch() {
    const searchInput = DOM.$('#search-input');
    if (!searchInput) return;

    this.searchInput = new Search({
      inputSelector: '#search-input',
      itemsSelector: '.course-item',
      searchAttribute: 'data-name',
      onSearch: (term) => {
        console.log('Buscando:', term);
      }
    });
  }

  /**
   * Configura el ordenamiento de cursos
   */
  setupSort() {
    this.sortSelect = DOM.$('#sort-select');
    if (!this.sortSelect) return;

    this.sortSelect.addEventListener('change', (e) => {
      this.sortCourses(e.target.value);
    });
  }

  /**
   * Ordena los cursos según el criterio seleccionado
   */
  sortCourses(criteria) {
    const courseGrid = DOM.$('.course-grid');
    if (!courseGrid) return;

    const courses = Array.from(courseGrid.children);

    courses.sort((a, b) => {
      if (criteria === 'name') {
        const nameA = a.getAttribute('data-name') || '';
        const nameB = b.getAttribute('data-name') || '';
        return nameA.localeCompare(nameB);
      } else if (criteria === 'price') {
        const priceA = parseFloat(a.getAttribute('data-price')) || 0;
        const priceB = parseFloat(b.getAttribute('data-price')) || 0;
        return priceA - priceB;
      } else if (criteria === 'date') {
        // Si tienes fecha en data-attribute
        const dateA = a.getAttribute('data-date') || '';
        const dateB = b.getAttribute('data-date') || '';
        return dateB.localeCompare(dateA); // Más recientes primero
      }
      return 0;
    });

    // Reordenar en el DOM
    courses.forEach(course => courseGrid.appendChild(course));
  }
}

// Auto-inicialización si estamos en la página dashboard
DOM.ready(() => {
  if (document.body.classList.contains('page-dashboard') ||
      window.location.pathname.includes('dashboard')) {
    new DashboardPage();
  }
});
