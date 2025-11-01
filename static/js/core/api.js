/**
 * API Core Module
 * Maneja todas las peticiones HTTP y configuración de CSRF
 */

class API {
  constructor() {
    this.csrfToken = this.getCSRFToken();
  }

  /**
   * Obtiene el token CSRF del meta tag
   */
  getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.content : '';
  }

  /**
   * Headers por defecto para peticiones
   */
  getDefaultHeaders() {
    return {
      'Content-Type': 'application/json',
      'X-CSRFToken': this.csrfToken
    };
  }

  /**
   * Petición GET genérica
   */
  async get(url, params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const fullUrl = queryString ? `${url}?${queryString}` : url;

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('GET request failed:', error);
      throw error;
    }
  }

  /**
   * Petición POST genérica
   */
  async post(url, data = {}) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.getDefaultHeaders(),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('POST request failed:', error);
      throw error;
    }
  }

  /**
   * Petición PUT genérica
   */
  async put(url, data = {}) {
    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: this.getDefaultHeaders(),
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('PUT request failed:', error);
      throw error;
    }
  }

  /**
   * Petición DELETE genérica
   */
  async delete(url) {
    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getDefaultHeaders()
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('DELETE request failed:', error);
      throw error;
    }
  }
}

// Exportar instancia única
export const api = new API();
