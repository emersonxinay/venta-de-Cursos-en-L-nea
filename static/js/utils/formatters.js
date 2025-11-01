/**
 * Formatters Utilities
 * Funciones para formatear datos
 */

export const Formatters = {
  /**
   * Formatea número como moneda
   */
  currency(value, symbol = '$') {
    const num = parseFloat(value) || 0;
    return `${symbol}${num.toFixed(2)}`;
  },

  /**
   * Formatea fecha
   */
  date(dateString, format = 'DD/MM/YYYY') {
    const date = new Date(dateString);

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    return format
      .replace('DD', day)
      .replace('MM', month)
      .replace('YYYY', year);
  },

  /**
   * Formatea porcentaje
   */
  percentage(value, decimals = 0) {
    const num = parseFloat(value) || 0;
    return `${num.toFixed(decimals)}%`;
  },

  /**
   * Trunca texto
   */
  truncate(text, length = 50, suffix = '...') {
    if (text.length <= length) return text;
    return text.substring(0, length) + suffix;
  },

  /**
   * Capitaliza primera letra
   */
  capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  },

  /**
   * Formatea duración en minutos
   */
  duration(minutes) {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  }
};
