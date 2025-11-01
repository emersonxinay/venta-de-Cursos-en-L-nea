/**
 * Main Entry Point
 * Punto de entrada principal de la aplicación
 */

// Importar módulo principal
import './core/app.js';

// Importar utilidades de lazy loading
import './utils/lazy-load.js';

// Importar páginas (se auto-inicializan según el contexto)
import './pages/dashboard.js';
import './pages/admin-dashboard.js';
import './pages/course-view.js';
import './pages/auth.js';

// Exportar utilidades globales para uso en templates si es necesario
import { DOM } from './utils/dom.js';
import { Formatters } from './utils/formatters.js';
import { Animations } from './utils/animations.js';
import { api } from './core/api.js';
import { showNotification } from './core/app.js';
import { loadModule, loadCSS } from './utils/lazy-load.js';

// Hacer disponibles globalmente si se necesita acceso desde templates
window.CompilandoCode = {
  DOM,
  Formatters,
  Animations,
  api,
  showNotification,
  loadModule,
  loadCSS
};

console.log('📦 Módulos JavaScript cargados correctamente');
console.log('⚡ Lazy loading enabled');
