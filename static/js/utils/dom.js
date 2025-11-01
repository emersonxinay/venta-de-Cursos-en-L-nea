/**
 * DOM Utilities
 * Helpers para manipulación del DOM
 */

export const DOM = {
  /**
   * Selector seguro que retorna elemento o null
   */
  $(selector, context = document) {
    return context.querySelector(selector);
  },

  /**
   * Selector que retorna todos los elementos
   */
  $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  },

  /**
   * Agrega clase(s) a un elemento
   */
  addClass(element, ...classes) {
    if (element) {
      element.classList.add(...classes);
    }
  },

  /**
   * Remueve clase(s) de un elemento
   */
  removeClass(element, ...classes) {
    if (element) {
      element.classList.remove(...classes);
    }
  },

  /**
   * Toggle clase en un elemento
   */
  toggleClass(element, className) {
    if (element) {
      element.classList.toggle(className);
    }
  },

  /**
   * Verifica si un elemento tiene una clase
   */
  hasClass(element, className) {
    return element ? element.classList.contains(className) : false;
  },

  /**
   * Muestra un elemento
   */
  show(element, display = 'block') {
    if (element) {
      element.style.display = display;
    }
  },

  /**
   * Oculta un elemento
   */
  hide(element) {
    if (element) {
      element.style.display = 'none';
    }
  },

  /**
   * Toggle visibilidad de un elemento
   */
  toggle(element, display = 'block') {
    if (element) {
      element.style.display = element.style.display === 'none' ? display : 'none';
    }
  },

  /**
   * Agrega event listener con soporte para delegación
   */
  on(element, event, selectorOrHandler, handler) {
    if (typeof selectorOrHandler === 'function') {
      element.addEventListener(event, selectorOrHandler);
    } else {
      element.addEventListener(event, (e) => {
        if (e.target.matches(selectorOrHandler)) {
          handler.call(e.target, e);
        }
      });
    }
  },

  /**
   * Crea un elemento con atributos y contenido
   */
  createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);

    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'class') {
        element.className = value;
      } else if (key === 'style' && typeof value === 'object') {
        Object.assign(element.style, value);
      } else {
        element.setAttribute(key, value);
      }
    });

    if (content) {
      element.innerHTML = content;
    }

    return element;
  },

  /**
   * Normaliza texto removiendo acentos
   */
  normalizeText(text) {
    return text
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  },

  /**
   * Ejecuta callback cuando el DOM esté listo
   */
  ready(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback);
    } else {
      callback();
    }
  }
};
