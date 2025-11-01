/**
 * Animations Utilities
 * Funciones para animaciones reutilizables
 */

export const Animations = {
  /**
   * Anima un valor numérico (contador)
   */
  animateValue(element, start, end, duration = 1000) {
    if (!element) return;

    let startTimestamp = null;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);

      element.textContent = current;

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    window.requestAnimationFrame(step);
  },

  /**
   * Anima valor monetario
   */
  animateCurrency(element, start, end, duration = 1000, symbol = '$') {
    if (!element) return;

    let startTimestamp = null;

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);

      element.textContent = `${symbol}${current}`;

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    window.requestAnimationFrame(step);
  },

  /**
   * Fade in elemento
   */
  fadeIn(element, duration = 300) {
    if (!element) return;

    element.style.opacity = 0;
    element.style.display = 'block';

    let start = null;

    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = (timestamp - start) / duration;

      element.style.opacity = Math.min(progress, 1);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  },

  /**
   * Fade out elemento
   */
  fadeOut(element, duration = 300) {
    if (!element) return;

    let start = null;

    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = (timestamp - start) / duration;

      element.style.opacity = Math.max(1 - progress, 0);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        element.style.display = 'none';
      }
    };

    requestAnimationFrame(animate);
  },

  /**
   * Slide down elemento
   */
  slideDown(element, duration = 300) {
    if (!element) return;

    element.style.removeProperty('display');
    let display = window.getComputedStyle(element).display;
    if (display === 'none') display = 'block';
    element.style.display = display;

    const height = element.offsetHeight;
    element.style.overflow = 'hidden';
    element.style.height = 0;
    element.style.paddingTop = 0;
    element.style.paddingBottom = 0;
    element.style.marginTop = 0;
    element.style.marginBottom = 0;

    element.offsetHeight; // Force reflow
    element.style.transition = `all ${duration}ms ease-out`;
    element.style.height = height + 'px';
    element.style.removeProperty('padding-top');
    element.style.removeProperty('padding-bottom');
    element.style.removeProperty('margin-top');
    element.style.removeProperty('margin-bottom');

    setTimeout(() => {
      element.style.removeProperty('height');
      element.style.removeProperty('overflow');
      element.style.removeProperty('transition');
    }, duration);
  },

  /**
   * Slide up elemento
   */
  slideUp(element, duration = 300) {
    if (!element) return;

    element.style.height = element.offsetHeight + 'px';
    element.offsetHeight; // Force reflow
    element.style.overflow = 'hidden';
    element.style.transition = `all ${duration}ms ease-out`;
    element.style.height = 0;
    element.style.paddingTop = 0;
    element.style.paddingBottom = 0;
    element.style.marginTop = 0;
    element.style.marginBottom = 0;

    setTimeout(() => {
      element.style.display = 'none';
      element.style.removeProperty('height');
      element.style.removeProperty('padding-top');
      element.style.removeProperty('padding-bottom');
      element.style.removeProperty('margin-top');
      element.style.removeProperty('margin-bottom');
      element.style.removeProperty('overflow');
      element.style.removeProperty('transition');
    }, duration);
  }
};
