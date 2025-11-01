/**
 * Auth Pages Module
 * Lógica para páginas de autenticación (login/register)
 */

import { DOM } from '../utils/dom.js';

export class AuthPage {
  constructor() {
    this.init();
  }

  init() {
    this.setupPasswordToggle();
    this.setupFormValidation();
  }

  /**
   * Toggle visibilidad de contraseña
   */
  setupPasswordToggle() {
    const toggleButtons = DOM.$$('[data-password-toggle]');

    toggleButtons.forEach(button => {
      button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-password-toggle');
        const input = DOM.$(`#${targetId}`);

        if (!input) return;

        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);

        // Cambiar icono si existe
        const icon = DOM.$('svg', button);
        if (icon) {
          // Aquí podrías cambiar el icono
          button.setAttribute('aria-label', type === 'password' ? 'Mostrar contraseña' : 'Ocultar contraseña');
        }
      });
    });
  }

  /**
   * Validación básica de formularios
   */
  setupFormValidation() {
    const forms = DOM.$$('form[data-validate]');

    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
          return false;
        }
      });
    });
  }

  /**
   * Valida un formulario
   */
  validateForm(form) {
    let isValid = true;
    const inputs = DOM.$$('input[required], select[required], textarea[required]', form);

    inputs.forEach(input => {
      if (!input.value.trim()) {
        this.showError(input, 'Este campo es requerido');
        isValid = false;
      } else {
        this.clearError(input);
      }

      // Validación de email
      if (input.type === 'email' && input.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
          this.showError(input, 'Email inválido');
          isValid = false;
        }
      }

      // Validación de contraseña
      if (input.type === 'password' && input.value) {
        if (input.value.length < 6) {
          this.showError(input, 'La contraseña debe tener al menos 6 caracteres');
          isValid = false;
        }
      }

      // Confirmación de contraseña
      if (input.name === 'confirm_password') {
        const password = DOM.$('input[name="password"]', form);
        if (password && input.value !== password.value) {
          this.showError(input, 'Las contraseñas no coinciden');
          isValid = false;
        }
      }
    });

    return isValid;
  }

  /**
   * Muestra error en un input
   */
  showError(input, message) {
    this.clearError(input);

    DOM.addClass(input, 'border-red-500');

    const errorDiv = DOM.createElement('div', {
      class: 'text-red-500 text-sm mt-1 error-message'
    }, message);

    input.parentElement.appendChild(errorDiv);
  }

  /**
   * Limpia error de un input
   */
  clearError(input) {
    DOM.removeClass(input, 'border-red-500');

    const errorMessage = DOM.$('.error-message', input.parentElement);
    if (errorMessage) {
      errorMessage.remove();
    }
  }
}

// Auto-inicialización
DOM.ready(() => {
  if (document.body.classList.contains('page-login') ||
      document.body.classList.contains('page-register') ||
      window.location.pathname.includes('/login') ||
      window.location.pathname.includes('/register')) {
    new AuthPage();
  }
});
