/**
 * Lazy Loading Utilities
 * Para cargar imágenes y recursos pesados solo cuando sean necesarios
 */

import { DOM } from './dom.js';

export class LazyLoader {
  constructor() {
    this.observer = null;
    this.init();
  }

  init() {
    // Usar Intersection Observer si está disponible
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              this.loadElement(entry.target);
              this.observer.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: '50px' // Empezar a cargar 50px antes de que sea visible
        }
      );

      this.observeElements();
    } else {
      // Fallback: cargar todo inmediatamente
      this.loadAll();
    }
  }

  /**
   * Observa elementos con lazy loading
   */
  observeElements() {
    // Imágenes con data-src
    DOM.$$('img[data-src]').forEach(img => {
      this.observer.observe(img);
    });

    // Iframes con data-src (videos, etc)
    DOM.$$('iframe[data-src]').forEach(iframe => {
      this.observer.observe(iframe);
    });

    // Secciones con data-lazy
    DOM.$$('[data-lazy]').forEach(section => {
      this.observer.observe(section);
    });
  }

  /**
   * Carga un elemento específico
   */
  loadElement(element) {
    if (element.tagName === 'IMG') {
      this.loadImage(element);
    } else if (element.tagName === 'IFRAME') {
      this.loadIframe(element);
    } else if (element.hasAttribute('data-lazy')) {
      this.loadSection(element);
    }
  }

  /**
   * Carga una imagen lazy
   */
  loadImage(img) {
    const src = img.getAttribute('data-src');
    const srcset = img.getAttribute('data-srcset');

    if (!src) return;

    // Crear imagen temporal para precargar
    const tempImg = new Image();

    tempImg.onload = () => {
      img.src = src;
      if (srcset) {
        img.srcset = srcset;
      }
      img.removeAttribute('data-src');
      img.removeAttribute('data-srcset');
      DOM.addClass(img, 'loaded');
    };

    tempImg.onerror = () => {
      console.error('Error loading image:', src);
      DOM.addClass(img, 'error');
    };

    tempImg.src = src;
  }

  /**
   * Carga un iframe lazy (videos, etc)
   */
  loadIframe(iframe) {
    const src = iframe.getAttribute('data-src');
    if (!src) return;

    iframe.src = src;
    iframe.removeAttribute('data-src');
    DOM.addClass(iframe, 'loaded');
  }

  /**
   * Carga una sección lazy
   */
  loadSection(section) {
    const lazyType = section.getAttribute('data-lazy');

    if (lazyType === 'chart') {
      // Cargar gráfico
      this.loadChart(section);
    } else if (lazyType === 'video') {
      // Cargar reproductor de video
      this.loadVideo(section);
    }

    section.removeAttribute('data-lazy');
    DOM.addClass(section, 'loaded');
  }

  /**
   * Carga un gráfico Chart.js
   */
  loadChart(section) {
    const chartId = section.getAttribute('data-chart-id');
    const chartData = section.getAttribute('data-chart-data');

    if (!chartId || !chartData) return;

    // Disparar evento para que el módulo de charts lo maneje
    section.dispatchEvent(new CustomEvent('lazy-chart-load', {
      detail: {
        chartId,
        chartData: JSON.parse(chartData)
      }
    }));
  }

  /**
   * Carga un reproductor de video
   */
  loadVideo(section) {
    const videoUrl = section.getAttribute('data-video-url');
    if (!videoUrl) return;

    // Disparar evento para que el módulo de video lo maneje
    section.dispatchEvent(new CustomEvent('lazy-video-load', {
      detail: { videoUrl }
    }));
  }

  /**
   * Carga todos los elementos inmediatamente (fallback)
   */
  loadAll() {
    DOM.$$('img[data-src]').forEach(img => this.loadImage(img));
    DOM.$$('iframe[data-src]').forEach(iframe => this.loadIframe(iframe));
    DOM.$$('[data-lazy]').forEach(section => this.loadSection(section));
  }

  /**
   * Agrega nuevos elementos para observar (útil para contenido dinámico)
   */
  observe(element) {
    if (this.observer) {
      this.observer.observe(element);
    } else {
      this.loadElement(element);
    }
  }
}

/**
 * Lazy load de módulos JavaScript
 */
export async function loadModule(modulePath) {
  try {
    const module = await import(modulePath);
    return module;
  } catch (error) {
    console.error(`Error loading module ${modulePath}:`, error);
    return null;
  }
}

/**
 * Lazy load de CSS
 */
export function loadCSS(href) {
  return new Promise((resolve, reject) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;

    link.onload = () => resolve(link);
    link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));

    document.head.appendChild(link);
  });
}

// Inicializar automáticamente
DOM.ready(() => {
  window.lazyLoader = new LazyLoader();
  console.log('✅ Lazy loader initialized');
});

export default LazyLoader;
