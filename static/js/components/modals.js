/**
 * Modal Component
 * Componente reutilizable para modales
 */

import { DOM } from '../utils/dom.js';
import { Animations } from '../utils/animations.js';

export class Modal {
  constructor(modalId) {
    this.modal = DOM.$(`#${modalId}`);
    this.closeButtons = [];
    this.onOpen = null;
    this.onClose = null;

    if (this.modal) {
      this.init();
    }
  }

  init() {
    // Buscar botones de cerrar
    this.closeButtons = DOM.$$('[data-modal-close]', this.modal);

    // Event listeners para cerrar
    this.closeButtons.forEach(btn => {
      btn.addEventListener('click', () => this.close());
    });

    // Cerrar al hacer click fuera del modal
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !DOM.hasClass(this.modal, 'hidden')) {
        this.close();
      }
    });
  }

  open() {
    DOM.removeClass(this.modal, 'hidden');
    Animations.fadeIn(this.modal, 200);
    document.body.style.overflow = 'hidden';

    if (this.onOpen) {
      this.onOpen();
    }
  }

  close() {
    DOM.addClass(this.modal, 'hidden');
    document.body.style.overflow = '';

    if (this.onClose) {
      this.onClose();
    }
  }

  toggle() {
    if (DOM.hasClass(this.modal, 'hidden')) {
      this.open();
    } else {
      this.close();
    }
  }

  setContent(content) {
    const body = DOM.$('.modal-body', this.modal);
    if (body) {
      body.innerHTML = content;
    }
  }
}

/**
 * Confirm Dialog
 * Modal de confirmación simple
 */
export class ConfirmDialog {
  static show(config) {
    return new Promise((resolve) => {
      const {
        title = '¿Estás seguro?',
        message = '',
        confirmText = 'Confirmar',
        cancelText = 'Cancelar',
        type = 'warning' // success, danger, warning, info
      } = config;

      // Crear modal dinámicamente
      const modalHTML = `
        <div id="confirm-dialog" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div class="card glass-effect max-w-md w-full m-4">
            <div class="card-body">
              <h3 class="text-xl font-bold text-white mb-3">${title}</h3>
              <p class="text-white/80 mb-6">${message}</p>
              <div class="flex gap-3 justify-end">
                <button id="confirm-cancel" class="btn-ghost-gradient">
                  ${cancelText}
                </button>
                <button id="confirm-ok" class="btn-gradient ${type}">
                  ${confirmText}
                </button>
              </div>
            </div>
          </div>
        </div>
      `;

      document.body.insertAdjacentHTML('beforeend', modalHTML);

      const modal = DOM.$('#confirm-dialog');
      const okBtn = DOM.$('#confirm-ok');
      const cancelBtn = DOM.$('#confirm-cancel');

      const cleanup = () => {
        modal.remove();
      };

      okBtn.addEventListener('click', () => {
        cleanup();
        resolve(true);
      });

      cancelBtn.addEventListener('click', () => {
        cleanup();
        resolve(false);
      });

      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          cleanup();
          resolve(false);
        }
      });
    });
  }
}
