/**
 * Search Component
 * Componente reutilizable para búsqueda y filtrado
 */

import { DOM } from '../utils/dom.js';

export class Search {
  constructor(config) {
    this.inputSelector = config.inputSelector;
    this.itemsSelector = config.itemsSelector;
    this.searchAttribute = config.searchAttribute || 'data-search';
    this.onSearch = config.onSearch || null;
    this.debounceTime = config.debounceTime || 300;
    this.caseSensitive = config.caseSensitive || false;

    this.input = DOM.$(this.inputSelector);
    this.debounceTimer = null;

    this.init();
  }

  init() {
    if (!this.input) {
      console.warn(`Search input not found: ${this.inputSelector}`);
      return;
    }

    this.input.addEventListener('input', (e) => this.handleSearch(e));
  }

  handleSearch(event) {
    clearTimeout(this.debounceTimer);

    this.debounceTimer = setTimeout(() => {
      const searchTerm = this.caseSensitive
        ? event.target.value
        : DOM.normalizeText(event.target.value);

      this.performSearch(searchTerm);

      if (this.onSearch) {
        this.onSearch(searchTerm);
      }
    }, this.debounceTime);
  }

  performSearch(searchTerm) {
    const items = DOM.$$(this.itemsSelector);

    items.forEach(item => {
      const searchText = this.caseSensitive
        ? item.getAttribute(this.searchAttribute) || ''
        : DOM.normalizeText(item.getAttribute(this.searchAttribute) || '');

      if (searchTerm === '' || searchText.includes(searchTerm)) {
        DOM.show(item);
      } else {
        DOM.hide(item);
      }
    });
  }

  clear() {
    if (this.input) {
      this.input.value = '';
      this.performSearch('');
    }
  }
}

/**
 * Table Search Component
 * Búsqueda específica para tablas
 */
export class TableSearch {
  constructor(inputId, tableId) {
    this.searchInput = DOM.$(`#${inputId}`);
    this.table = DOM.$(`#${tableId}`);

    if (!this.searchInput || !this.table) {
      console.warn(`Table search initialization failed: input=${inputId}, table=${tableId}`);
      return;
    }

    this.rows = DOM.$$('tbody tr', this.table);
    this.init();
  }

  init() {
    this.searchInput.addEventListener('input', (e) => {
      const searchTerm = DOM.normalizeText(e.target.value);
      this.filter(searchTerm);
    });
  }

  filter(searchTerm) {
    this.rows.forEach(row => {
      const searchText = DOM.normalizeText(row.getAttribute('data-search') || '');
      row.style.display = searchTerm === '' || searchText.includes(searchTerm) ? '' : 'none';
    });
  }
}
