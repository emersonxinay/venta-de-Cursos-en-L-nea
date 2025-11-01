# 🏗️ Arquitectura Frontend - CompilandoCode

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Sistema JavaScript Modular](#sistema-javascript-modular)
- [Sistema CSS Modular](#sistema-css-modular)
- [Guía de Implementación](#guía-de-implementación)
- [Migración desde Templates](#migración-desde-templates)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Visión General

Este proyecto ha sido refactorizado para usar una arquitectura frontend **modular y escalable**:

### Antes ❌

```html
{% block extra_js %}
<script>
  // 200 líneas de JS embebido...
  document.addEventListener('DOMContentLoaded', function() {
    // Código duplicado en múltiples templates
  });
</script>
{% endblock %}
```

### Ahora ✅

```html
<script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>
<!-- Todo el JS modular se carga automáticamente -->
```

## Estructura de Carpetas

```
static/
├── css/
│   ├── app.css                 # 🎯 Punto de entrada CSS
│   ├── base/                   # Variables y configuración
│   ├── components/             # Componentes UI reutilizables
│   ├── pages/                  # Estilos específicos por página
│   ├── utilities/              # Utilidades (animaciones, etc)
│   └── README.md               # Documentación CSS
│
├── js/
│   ├── main.js                 # 🎯 Punto de entrada JavaScript
│   ├── core/                   # Módulos principales (API, App)
│   ├── utils/                  # Utilidades (DOM, Formatters, Animations)
│   ├── components/             # Componentes (Search, Charts, Modals, VideoPlayer)
│   ├── pages/                  # Lógica específica por página
│   └── README.md               # Documentación JS
│
└── uploads/                    # Archivos subidos
```

## Sistema JavaScript Modular

### Módulos Principales

#### 1. **Core Modules** (`js/core/`)

```javascript
// API Client
import { api } from './core/api.js';
await api.get('/endpoint');
await api.post('/endpoint', { data });

// App (inicialización principal)
import { showNotification } from './core/app.js';
showNotification('¡Éxito!', 'success');
```

#### 2. **Utils** (`js/utils/`)

```javascript
// DOM Utilities
import { DOM } from './utils/dom.js';
const element = DOM.$('#myId');
DOM.addClass(element, 'active');

// Formatters
import { Formatters } from './utils/formatters.js';
Formatters.currency(99.99);  // "$99.99"

// Animations
import { Animations } from './utils/animations.js';
Animations.fadeIn(element, 300);
```

#### 3. **Components** (`js/components/`)

```javascript
// Search Component
import { Search } from './components/search.js';
new Search({
  inputSelector: '#search',
  itemsSelector: '.item'
});

// Charts
import { chartManager } from './components/charts.js';
chartManager.createBarChart('myChart', { /* config */ });

// Modals
import { Modal } from './components/modals.js';
const modal = new Modal('modal-id');
modal.open();

// Video Player
import { VideoPlayer } from './components/video-player.js';
new VideoPlayer(cursoId);
```

#### 4. **Pages** (`js/pages/`)

Auto-inicialización basada en clases del body:

```html
<body class="page-dashboard">
  <!-- DashboardPage se inicializa automáticamente -->
</body>
```

Páginas disponibles:
- `page-dashboard` → `dashboard.js`
- `page-admin-dashboard` → `admin-dashboard.js`
- `page-course-view` → `course-view.js`
- `page-login` / `page-register` → `auth.js`

## Sistema CSS Modular

### Archivo Principal

```html
<!-- Importa TODO el CSS en orden correcto -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

### Variables CSS Disponibles

```css
/* Colores */
var(--color-primary)
var(--color-secondary)
var(--color-success)
var(--color-danger)

/* Degradados */
var(--gradient-primary)
var(--gradient-blue-purple)
var(--gradient-purple-pink)

/* Espaciado */
var(--spacing-sm)
var(--spacing-md)
var(--spacing-lg)

/* Y muchas más... ver css/README.md */
```

### Clases Utilitarias

```html
<!-- Cards -->
<div class="card">Basic card</div>
<div class="gradient-card">Card con degradado</div>
<div class="glass-effect">Efecto glassmorphism</div>

<!-- Botones -->
<button class="btn-gradient">Botón degradado</button>
<button class="btn-ghost-gradient">Botón outline</button>

<!-- Animaciones -->
<div class="animate-fadeIn">Fade in</div>
<div class="hover-lift">Levanta al hover</div>
```

## Guía de Implementación

### 1. Base Template

Actualiza `base.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{% block title %}CompilandoCode{% endblock %}</title>

    <!-- CSS Principal -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">

    <!-- CSS extra por página -->
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% include 'shared/navbar.html' %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include 'shared/footer.html' %}

    <!-- JavaScript Modular -->
    <script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>

    <!-- JS extra por página -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. Template de Página Específica

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}

<!-- Clase para auto-inicialización -->
{% block body_class %}page-dashboard{% endblock %}

{% block content %}
<div class="container-fluid py-6">
    <div class="gradient-card">
        <div class="card-body">
            <h1>Dashboard</h1>

            <!-- Input de búsqueda -->
            <input
              id="search-input"
              type="text"
              placeholder="Buscar..."
              class="input-gradient"
            />

            <!-- Items buscables -->
            <div class="course-grid">
                {% for curso in cursos %}
                <div class="course-item card" data-name="{{ curso.nombre|lower }}">
                    {{ curso.nombre }}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

<!-- Si necesitas JS específico adicional -->
{% block extra_js %}
<script type="module">
  import { showNotification } from "{{ url_for('static', filename='js/core/app.js') }}";

  // Código específico de esta página
  document.querySelector('#mi-boton').addEventListener('click', () => {
    showNotification('¡Hecho!', 'success');
  });
</script>
{% endblock %}
```

### 3. Pasar Datos de Python a JavaScript

**Opción 1: Data Attributes (Recomendado)**

```html
<div
  id="curso-container"
  data-curso-id="{{ curso.id }}"
  data-curso-name="{{ curso.nombre }}"
  data-curso-price="{{ curso.precio }}"
>
</div>

<script type="module">
  const container = document.getElementById('curso-container');
  const cursoId = container.dataset.cursoId;
  const cursoName = container.dataset.cursoName;
</script>
```

**Opción 2: Variables Globales**

```html
<script>
  // Datos del template
  window.cursoId = {{ curso.id }};
  window.ventasNetasData = {
    dia: {{ ventas_netas_dia }},
    semana: {{ ventas_netas_semana }},
    mes: {{ ventas_netas_mes }},
    ano: {{ ventas_netas_ano }}
  };
</script>

<!-- Luego en módulos -->
<script type="module">
  import { chartManager } from './components/charts.js';

  chartManager.createBarChart('chart', {
    data: [
      window.ventasNetasData.dia,
      window.ventasNetasData.semana,
      // ...
    ]
  });
</script>
```

**Opción 3: JSON Endpoint**

```html
<script type="module">
  import { api } from './core/api.js';

  const data = await api.get('/api/dashboard-stats');
  console.log(data);
</script>
```

## Migración desde Templates

### Ejemplo Completo: Dashboard

#### Antes (dashboard.html old):

```html
{% extends "base.html" %}

{% block extra_css %}
<style>
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(1, 1fr);
    gap: 1rem;
  }
  /* 50+ líneas más... */
</style>
{% endblock %}

{% block content %}
<!-- HTML content -->
{% endblock %}

{% block extra_js %}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    // 100+ líneas de JavaScript...
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      const items = document.querySelectorAll('.course-item');
      items.forEach(item => {
        const name = item.getAttribute('data-name') || '';
        item.style.display = name.includes(searchTerm) ? 'block' : 'none';
      });
    });

    const sortSelect = document.getElementById('sort-select');
    sortSelect.addEventListener('change', function() {
      // Código de ordenamiento...
    });
  });
</script>
{% endblock %}
```

#### Después (dashboard.html new):

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block body_class %}page-dashboard{% endblock %}

{% block content %}
<div class="container-fluid py-6">
    <div class="gradient-card">
        <div class="card-body">
            <!-- Input de búsqueda - el componente Search se encarga -->
            <input id="search-input" type="text" placeholder="Buscar..." />

            <!-- Select de ordenamiento -->
            <select id="sort-select">
                <option value="name">Por nombre</option>
                <option value="price">Por precio</option>
            </select>

            <!-- Items -->
            <div class="course-grid">
                {% for curso in cursos %}
                <div
                  class="course-item card"
                  data-name="{{ curso.nombre|lower }}"
                  data-price="{{ curso.precio }}"
                >
                    {{ curso.nombre }}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

<!-- NO MÁS extra_js ni extra_css! -->
<!-- El módulo dashboard.js se carga automáticamente por la clase page-dashboard -->
```

**¡Resultado:**
- ❌ **0 líneas** de CSS inline
- ❌ **0 líneas** de JS inline
- ✅ Todo modular y reutilizable
- ✅ Auto-inicialización con `page-dashboard`

## Best Practices

### ✅ DO

1. **Usar variables CSS** para colores y espaciado
   ```css
   background: var(--color-primary);
   padding: var(--spacing-md);
   ```

2. **Usar clases de body** para auto-inicialización
   ```html
   <body class="page-dashboard">
   ```

3. **Data attributes** para pasar datos a JS
   ```html
   <div data-curso-id="{{ curso.id }}">
   ```

4. **Importar módulos** cuando necesites funcionalidad extra
   ```javascript
   import { Search } from './components/search.js';
   ```

5. **ES6+ syntax** - arrow functions, async/await, destructuring
   ```javascript
   const data = await api.get('/endpoint');
   const { id, name } = data;
   ```

### ❌ DON'T

1. **No duplicar código** - crear componente reutilizable
2. **No inline styles** - usar clases CSS
3. **No JavaScript embebido** - usar módulos
4. **No manipular DOM directo** - usar utilidades DOM
5. **No hardcodear valores** - usar variables CSS

## Troubleshooting

### Módulos no cargan

**Problema:** "Failed to load module script"

**Solución:** Asegúrate de usar `type="module"`:
```html
<script type="module" src="..."></script>
```

### CORS errors

**Problema:** "CORS policy blocked"

**Solución:** Los módulos deben servirse desde el mismo origen. Verifica que estés usando:
```python
url_for('static', filename='js/main.js')
```

### Variables globales no definidas

**Problema:** `cursoId is not defined`

**Solución:** Define antes de importar módulos:
```html
<script>
  window.cursoId = {{ curso.id }};
</script>
<script type="module" src="..."></script>
```

### Estilos no se aplican

**Problema:** Clases CSS no funcionan

**Solución:** Verifica que `app.css` esté cargado:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

### Funcionalidad no se auto-inicializa

**Problema:** DashboardPage no carga

**Solución:** Agrega clase al body:
```html
<body class="page-dashboard">
```

## 📚 Referencias

- [JS README](static/js/README.md) - Documentación JavaScript completa
- [CSS README](static/css/README.md) - Documentación CSS completa
- [MDN Web Docs](https://developer.mozilla.org/)
- [ES6 Modules](https://developer.mozilla.org/es/docs/Web/JavaScript/Guide/Modules)
- [CSS Variables](https://developer.mozilla.org/es/docs/Web/CSS/Using_CSS_custom_properties)

## 🚀 Próximos Pasos

1. **TypeScript**: Agregar tipos para mejor DX
2. **Build Process**: Webpack/Vite para bundling
3. **Testing**: Jest para unit tests
4. **Storybook**: Catálogo de componentes UI
5. **Pre-commit hooks**: Linting automático

---

**¿Preguntas?** Revisa los README específicos en `static/js/` y `static/css/`
