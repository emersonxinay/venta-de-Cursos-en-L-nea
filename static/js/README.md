# Sistema Modular de JavaScript - CompilandoCode

## 📁 Estructura de Carpetas

```
static/js/
├── core/               # Módulos principales del sistema
│   ├── api.js         # Manejo de peticiones HTTP y CSRF
│   └── app.js         # Inicialización principal
├── utils/             # Utilidades reutilizables
│   ├── dom.js         # Helpers para manipulación del DOM
│   ├── formatters.js  # Formateo de datos (moneda, fechas, etc)
│   └── animations.js  # Animaciones reutilizables
├── components/        # Componentes UI reutilizables
│   ├── search.js      # Componente de búsqueda/filtrado
│   ├── charts.js      # Wrapper para Chart.js
│   ├── modals.js      # Sistema de modales
│   └── video-player.js # Reproductor de video con tracking
├── pages/             # Lógica específica por página
│   ├── dashboard.js   # Dashboard principal
│   ├── admin-dashboard.js # Panel de administración
│   ├── course-view.js # Vista de curso
│   └── auth.js        # Login/Register
├── main.js            # Punto de entrada principal
└── README.md          # Esta documentación
```

## 🚀 Uso

### Opción 1: Importar en Base Template (Recomendado)

Agrega al final de `base.html` antes de `</body>`:

```html
<script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>
```

### Opción 2: Importar Módulos Específicos

Si solo necesitas funcionalidad específica en una página:

```html
<!-- Solo búsqueda -->
<script type="module">
  import { Search } from "{{ url_for('static', filename='js/components/search.js') }}";

  new Search({
    inputSelector: '#search-input',
    itemsSelector: '.course-item',
    searchAttribute: 'data-name'
  });
</script>
```

### Opción 3: Usar Utilidades Globales

Los módulos principales están disponibles globalmente en `window.CompilandoCode`:

```html
<script>
  // Usar API
  CompilandoCode.api.get('/api/cursos').then(data => {
    console.log(data);
  });

  // Mostrar notificación
  CompilandoCode.showNotification('¡Curso creado!', 'success');

  // Formatear moneda
  const precio = CompilandoCode.Formatters.currency(99.99);
</script>
```

## 📚 Documentación de Módulos

### Core/API

```javascript
import { api } from './core/api.js';

// GET request
const data = await api.get('/api/endpoint', { param: 'value' });

// POST request
const result = await api.post('/api/endpoint', { key: 'value' });

// PUT request
await api.put('/api/endpoint', { id: 1, name: 'Updated' });

// DELETE request
await api.delete('/api/endpoint/1');
```

### Utils/DOM

```javascript
import { DOM } from './utils/dom.js';

// Selectores
const element = DOM.$('#myId');
const elements = DOM.$$('.myClass');

// Clases
DOM.addClass(element, 'active');
DOM.removeClass(element, 'hidden');
DOM.toggleClass(element, 'visible');

// Visibilidad
DOM.show(element);
DOM.hide(element);
DOM.toggle(element);

// Crear elementos
const div = DOM.createElement('div', {
  class: 'card',
  id: 'myCard'
}, 'Contenido');

// Event listeners
DOM.on(element, 'click', () => console.log('clicked'));

// DOM Ready
DOM.ready(() => {
  console.log('DOM is ready');
});
```

### Utils/Formatters

```javascript
import { Formatters } from './utils/formatters.js';

Formatters.currency(99.99);        // "$99.99"
Formatters.date('2024-01-15');     // "15/01/2024"
Formatters.percentage(75.5, 1);    // "75.5%"
Formatters.truncate('Long text', 10); // "Long text..."
Formatters.capitalize('hello');    // "Hello"
Formatters.duration(125);          // "2h 5m"
```

### Utils/Animations

```javascript
import { Animations } from './utils/animations.js';

// Animar contador
Animations.animateValue(element, 0, 100, 1000);

// Animar moneda
Animations.animateCurrency(element, 0, 500, 1000, '$');

// Fade effects
Animations.fadeIn(element, 300);
Animations.fadeOut(element, 300);

// Slide effects
Animations.slideDown(element, 300);
Animations.slideUp(element, 300);
```

### Components/Search

```javascript
import { Search, TableSearch } from './components/search.js';

// Búsqueda general
const search = new Search({
  inputSelector: '#search-input',
  itemsSelector: '.course-item',
  searchAttribute: 'data-name',
  debounceTime: 300,
  onSearch: (term) => console.log('Searching:', term)
});

// Búsqueda en tablas
const tableSearch = new TableSearch('search-input-id', 'table-id');
```

### Components/Charts

```javascript
import { chartManager } from './components/charts.js';

// Gráfico de barras
chartManager.createBarChart('myChart', {
  labels: ['Ene', 'Feb', 'Mar'],
  data: [10, 20, 30],
  label: 'Ventas',
  yTicks: {
    callback: (value) => '$' + value
  }
});

// Gráfico de línea
chartManager.createLineChart('lineChart', {
  labels: ['Q1', 'Q2', 'Q3'],
  data: [100, 200, 150]
});

// Actualizar gráfico
chartManager.updateChart('myChart', [15, 25, 35]);

// Destruir gráfico
chartManager.destroyChart('myChart');
```

### Components/Modals

```javascript
import { Modal, ConfirmDialog } from './components/modals.js';

// Modal simple
const modal = new Modal('modal-id');
modal.open();
modal.close();
modal.setContent('<p>Nuevo contenido</p>');

// Dialog de confirmación
const confirmed = await ConfirmDialog.show({
  title: '¿Eliminar curso?',
  message: 'Esta acción no se puede deshacer',
  confirmText: 'Eliminar',
  cancelText: 'Cancelar',
  type: 'danger'
});

if (confirmed) {
  // Usuario confirmó
}
```

### Components/VideoPlayer

```javascript
import { VideoPlayer } from './components/video-player.js';

// Se auto-inicializa en la página de curso
const player = new VideoPlayer(cursoId);
```

## 🎯 Clases CSS para Auto-Inicialización

Las páginas se auto-inicializan si el body tiene estas clases:

- `page-dashboard` → Inicializa DashboardPage
- `page-admin-dashboard` → Inicializa AdminDashboardPage
- `page-course-view` → Inicializa CourseViewPage
- `page-login` o `page-register` → Inicializa AuthPage

Ejemplo en template:

```html
<body class="page-dashboard">
  <!-- El módulo de dashboard se cargará automáticamente -->
</body>
```

## 🔄 Migración desde Templates

### Antes (Embebido en template):

```html
{% block extra_js %}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function() {
      // búsqueda...
    });
  });
</script>
{% endblock %}
```

### Después (Modular):

```html
<!-- En base.html -->
<script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>

<!-- O si necesitas código específico: -->
{% block extra_js %}
<script type="module">
  import { Search } from "{{ url_for('static', filename='js/components/search.js') }}";
  new Search({
    inputSelector: '#search-input',
    itemsSelector: '.item'
  });
</script>
{% endblock %}
```

## ⚡ Beneficios

✅ **Código reutilizable** - No más duplicación
✅ **Fácil mantenimiento** - Cambios en un solo lugar
✅ **Type safety** - Compatible con TypeScript
✅ **Bundle friendly** - Listo para webpack/vite
✅ **Tree shaking** - Solo carga lo que se usa
✅ **Moderno** - ES6+ modules
✅ **Escalable** - Fácil agregar nuevos módulos

## 🛠️ Desarrollo

### Agregar nuevo componente:

1. Crear archivo en `components/nuevo-componente.js`
2. Exportar clase o función
3. Importar en `main.js` si es global
4. Documentar en este README

### Agregar nueva página:

1. Crear archivo en `pages/nueva-pagina.js`
2. Implementar auto-inicialización
3. Importar en `main.js`
4. Agregar clase al body del template correspondiente

## 📦 Build para Producción (Futuro)

```bash
# Instalar bundler (opcional)
npm install -g esbuild

# Build
esbuild static/js/main.js --bundle --minify --outfile=static/js/dist/main.min.js
```

## 🐛 Debug

```javascript
// En consola del navegador
console.log(window.CompilandoCode);

// Ver módulos cargados
console.log(Object.keys(window.CompilandoCode));
```
