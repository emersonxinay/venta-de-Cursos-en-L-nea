/**
 * App Core Module
 * Inicialización principal de la aplicación
 */

import { DOM } from '../utils/dom.js';

class App {
  constructor() {
    this.init();
  }

  init() {
    console.log('🚀 CompilandoCode App iniciada');

    this.setupGlobalEventListeners();
    this.setupNavbar();
    this.setupTheme();
    this.setupAnimations();
  }

  /**
   * Event listeners globales
   */
  setupGlobalEventListeners() {
    // Prevenir submit accidental de formularios
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        const form = e.target.closest('form');
        if (form && !form.hasAttribute('data-allow-enter')) {
          e.preventDefault();
        }
      }
    });

    // Confirmación antes de eliminar
    const deleteButtons = DOM.$$('button[type="submit"][onclick*="confirm"], a[onclick*="confirm"]');
    deleteButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const message = btn.getAttribute('data-confirm') || '¿Estás seguro de eliminar este elemento?';
        if (!confirm(message)) {
          e.preventDefault();
          return false;
        }
      });
    });
  }

  /**
   * Configuración de la navbar
   */
  setupNavbar() {
    // Mobile menu toggle
    const mobileMenuButton = DOM.$('[data-mobile-menu-toggle]');
    const mobileMenu = DOM.$('#mobile-menu');

    if (mobileMenuButton && mobileMenu) {
      mobileMenuButton.addEventListener('click', () => {
        DOM.toggleClass(mobileMenu, 'hidden');
      });
    }

    // Dropdown menus
    const dropdowns = DOM.$$('[data-dropdown-toggle]');
    dropdowns.forEach(toggle => {
      const targetId = toggle.getAttribute('data-dropdown-toggle');
      const menu = DOM.$(`#${targetId}`);

      if (!menu) return;

      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        DOM.toggleClass(menu, 'hidden');
      });

      // Cerrar al hacer click fuera
      document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
          DOM.addClass(menu, 'hidden');
        }
      });
    });
  }

  /**
   * Configuración de tema (dark/light mode)
   */
  setupTheme() {
    const themeToggle = DOM.$('[data-theme-toggle]');
    if (!themeToggle) return;

    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', () => {
      const theme = document.documentElement.getAttribute('data-theme');
      const newTheme = theme === 'dark' ? 'light' : 'dark';

      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    });
  }

  /**
   * Configuración de animaciones scroll
   */
  setupAnimations() {
    const animatedElements = DOM.$$('[data-animate]');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const animation = entry.target.getAttribute('data-animate');
          DOM.addClass(entry.target, animation || 'animate-fadeIn');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });

    animatedElements.forEach(el => observer.observe(el));
  }

  /**
   * Muestra notificación global
   */
  static showNotification(message, type = 'info') {
    const notification = DOM.createElement('div', {
      class: `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm notification-${type}`,
      style: {
        backgroundColor: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'
      }
    }, `
      <div class="flex items-center gap-3 text-white">
        <span>${message}</span>
        <button class="ml-auto" onclick="this.parentElement.parentElement.remove()">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `);

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 5000);
  }
}

// Exportar funciones útiles
export const showNotification = App.showNotification;

// Inicializar app cuando el DOM esté listo
DOM.ready(() => {
  window.App = new App();
});

export default App;
