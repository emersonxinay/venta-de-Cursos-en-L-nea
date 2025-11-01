# 🚀 Guía Rápida - Frontend Modularizado

## ⚡ Quick Start

### 1. Crear Nueva Página

```html
{% extends "base.html" %}
{% block title %}Mi Página{% endblock %}
{% block body_class %}page-mipagina{% endblock %}

{% block content %}
<div class="container-fluid py-6">
    <!-- Tu contenido aquí -->
</div>
{% endblock %}
```

**¡Ya está!** No necesitas CSS ni JS adicional.

---

## 🎨 Componentes UI Disponibles

### Cards

```html
<!-- Card básica -->
<div class="card">
    <div class="card-body">
        <h3>Título</h3>
        <p>Contenido</p>
    </div>
</div>

<!-- Card con degradado -->
<div class="gradient-card">
    <div class="gradient-card-body">
        <h3 class="text-white">Título</h3>
    </div>
</div>

<!-- Card mejorada con efecto hover -->
<div class="card-enhanced hover-lift">
    <div class="card-body">
        <h3>Hover para ver efecto</h3>
    </div>
</div>

<!-- Glass effect -->
<div class="glass-modern p-6 rounded-xl">
    <h3>Glassmorphism</h3>
</div>
```

### Botones

```html
<!-- Botón con degradado -->
<button class="btn-gradient">
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
    </svg>
    Crear Nuevo
</button>

<!-- Botón outline -->
<button class="btn-ghost-gradient">
    Cancelar
</button>

<!-- Botón con ripple effect -->
<button class="btn btn-gradient btn-ripple">
    Click Me
</button>

<!-- Tamaños -->
<button class="btn-gradient btn-sm">Pequeño</button>
<button class="btn-gradient btn-md">Mediano</button>
<button class="btn-gradient btn-lg">Grande</button>
```

### Inputs

```html
<!-- Input básico mejorado -->
<div class="input-enhanced">
    <label for="email">Email</label>
    <input type="email" id="email" placeholder="tu@email.com" />
</div>

<!-- Input con floating label -->
<div class="input-floating">
    <input type="text" id="name" placeholder=" " />
    <label for="name">Nombre completo</label>
</div>

<!-- Input con icono -->
<div class="input-group">
    <div class="input-icon">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
    </div>
    <input type="text" class="input-gradient" placeholder="Buscar..." />
</div>
```

### Badges

```html
<!-- Badges con colores -->
<span class="badge-gradient primary">Nuevo</span>
<span class="badge-gradient success">Activo</span>
<span class="badge-gradient warning">Pendiente</span>
<span class="badge-gradient danger">Cancelado</span>

<!-- Badge con dot -->
<span class="badge badge-success badge-dot">En línea</span>
```

### Progress Bars

```html
<!-- Progress bar moderna -->
<div class="progress-modern">
    <div class="progress-modern-fill" style="width: 75%;"></div>
</div>

<!-- Progress bar tradicional -->
<div class="progress-bar">
    <div class="progress-fill" style="width: 60%; background: var(--gradient-blue-purple);"></div>
</div>
```

### Alerts

```html
<!-- Alert moderna -->
<div class="alert-modern alert-modern-success">
    <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
    </svg>
    <div>
        <strong>¡Éxito!</strong> Tu operación se completó correctamente.
    </div>
</div>
```

### Tablas

```html
<table class="table-modern">
    <thead>
        <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Juan Pérez</td>
            <td>juan@example.com</td>
            <td><span class="badge-success">Admin</span></td>
        </tr>
    </tbody>
</table>
```

### Dropdowns

```html
<div class="dropdown-modern">
    <button class="btn-gradient" onclick="toggleDropdown('dropdown1')">
        Opciones
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
    </button>

    <div id="dropdown1" class="dropdown-modern-menu">
        <a href="#" class="dropdown-modern-item">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Editar
        </a>
        <a href="#" class="dropdown-modern-item">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            Eliminar
        </a>
    </div>
</div>

<script>
function toggleDropdown(id) {
    const dropdown = document.getElementById(id);
    dropdown.classList.toggle('show');
}
</script>
```

### Tooltips

```html
<button class="btn-gradient" data-tooltip="Haz click para crear">
    Crear
</button>
```

### Empty States

```html
<div class="empty-state">
    <div class="empty-state-icon">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
        </svg>
    </div>
    <h3 class="empty-state-title">No hay cursos disponibles</h3>
    <p class="empty-state-description">Empieza creando tu primer curso</p>
    <button class="btn-gradient">
        Crear Curso
    </button>
</div>
```

### Loading States

```html
<!-- Spinner -->
<div class="flex items-center justify-center py-12">
    <div class="spinner"></div>
</div>

<!-- Skeleton loading -->
<div class="skeleton h-40 rounded-xl mb-4"></div>
<div class="skeleton h-4 w-3/4 rounded mb-2"></div>
<div class="skeleton h-4 w-1/2 rounded"></div>
```

---

## 💅 Clases Utilitarias

### Layout

```html
<!-- Container fluido con padding responsivo -->
<div class="container-fluid py-6">...</div>

<!-- Grid responsivo -->
<div class="grid-responsive">
    <div class="card">Item 1</div>
    <div class="card">Item 2</div>
    <div class="card">Item 3</div>
</div>

<!-- Flexbox helpers -->
<div class="flex items-center justify-between gap-4">...</div>
```

### Animaciones

```html
<!-- Fade in -->
<div class="animate-fadeIn">Contenido</div>

<!-- Fade in desde abajo -->
<div class="animate-fadeInUp delay-200">Contenido con delay</div>

<!-- Hover lift effect -->
<div class="hover-lift">Se eleva al hacer hover</div>

<!-- Transiciones -->
<div class="transition-smooth">Transición suave</div>
<div class="transition-fast">Transición rápida</div>
```

### Colores (Variables CSS)

```css
/* Colores principales */
var(--color-primary)    /* #6366f1 - Azul */
var(--color-secondary)  /* #8b5cf6 - Morado */
var(--color-success)    /* #10b981 - Verde */
var(--color-warning)    /* #f59e0b - Amarillo */
var(--color-danger)     /* #ef4444 - Rojo */

/* Degradados */
var(--gradient-primary)
var(--gradient-blue-purple)
var(--gradient-purple-pink)
var(--gradient-orange-amber)
var(--gradient-emerald-teal)

/* Espaciado */
var(--spacing-sm)   /* 0.5rem */
var(--spacing-md)   /* 1rem */
var(--spacing-lg)   /* 1.5rem */
var(--spacing-xl)   /* 2rem */

/* Bordes */
var(--radius-sm)    /* 0.375rem */
var(--radius-md)    /* 0.5rem */
var(--radius-lg)    /* 0.75rem */
var(--radius-xl)    /* 1rem */
var(--radius-full)  /* 9999px */
```

---

## 🔧 JavaScript Útil

### Usar Componentes

```html
<script type="module">
  import { Search } from "{{ url_for('static', filename='js/components/search.js') }}";
  import { showNotification } from "{{ url_for('static', filename='js/core/app.js') }}";

  // Búsqueda
  new Search({
    inputSelector: '#search-input',
    itemsSelector: '.course-item',
    searchAttribute: 'data-name'
  });

  // Notificación
  showNotification('¡Operación exitosa!', 'success');
</script>
```

### Usar API

```html
<script type="module">
  import { api } from "{{ url_for('static', filename='js/core/api.js') }}";

  // GET
  const cursos = await api.get('/api/cursos');

  // POST
  const resultado = await api.post('/api/cursos', {
    nombre: 'Nuevo Curso',
    precio: 99.99
  });
</script>
```

### Utilidades Globales

```html
<script>
  // Disponibles directamente
  CompilandoCode.Formatters.currency(99.99);  // "$99.99"
  CompilandoCode.Formatters.date('2024-01-15'); // "15/01/2024"

  CompilandoCode.showNotification('Mensaje', 'success');

  CompilandoCode.api.get('/endpoint').then(console.log);
</script>
```

---

## 📋 Checklist para Nueva Página

- [ ] Extender `base.html`
- [ ] Agregar `{% block body_class %}page-nombre{% endblock %}`
- [ ] Usar componentes UI existentes (cards, buttons, etc.)
- [ ] Usar variables CSS en lugar de colores hardcoded
- [ ] Agregar data attributes para JavaScript
- [ ] Probar responsive design (mobile first)
- [ ] Verificar dark mode si aplica
- [ ] Comprobar accesibilidad (focus, aria-labels)

---

## 🎯 Ejemplos Completos

### Formulario Completo

```html
<div class="card-enhanced">
    <div class="card-body">
        <h2 class="text-2xl font-bold mb-6">Crear Curso</h2>

        <form class="space-y-4">
            <!-- Nombre -->
            <div class="input-enhanced">
                <label for="nombre">Nombre del Curso</label>
                <input type="text" id="nombre" required />
            </div>

            <!-- Descripción -->
            <div class="input-enhanced">
                <label for="descripcion">Descripción</label>
                <textarea id="descripcion" rows="4"></textarea>
            </div>

            <!-- Precio -->
            <div class="input-floating">
                <input type="number" id="precio" placeholder=" " />
                <label for="precio">Precio (USD)</label>
            </div>

            <!-- Botones -->
            <div class="flex gap-3 justify-end">
                <button type="button" class="btn-ghost-gradient">
                    Cancelar
                </button>
                <button type="submit" class="btn-gradient">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Guardar
                </button>
            </div>
        </form>
    </div>
</div>
```

### Grid de Cards

```html
<div class="grid-responsive">
    {% for curso in cursos %}
    <div class="card-enhanced hover-lift">
        <div class="card-body">
            <div class="flex items-start justify-between mb-3">
                <h3 class="font-semibold">{{ curso.nombre }}</h3>
                <span class="badge-gradient success">Activo</span>
            </div>

            <p class="text-sm text-gray-600 mb-4">{{ curso.descripcion }}</p>

            <div class="flex items-center justify-between">
                <span class="text-2xl font-bold text-primary-600">
                    ${{ curso.precio }}
                </span>
                <button class="btn-gradient btn-sm">
                    Ver Curso
                </button>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
```

---

## 🚨 Problemas Comunes

### Los estilos no se aplican

**Solución:** Verifica que base.html tenga todos los CSS cargados:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}" />
<link rel="stylesheet" href="{{ url_for('static', filename='css/design-system.css') }}" />
<!-- ... etc -->
```

### JavaScript no funciona

**Solución:** Usa `type="module"` en scripts:
```html
<script type="module" src="{{ url_for('static', filename='js/main.js') }}"></script>
```

### Componentes no tienen efecto hover

**Solución:** Agrega clase `hover-lift`:
```html
<div class="card-enhanced hover-lift">...</div>
```

---

**¿Más ayuda?**
- Ver `FRONTEND_ARCHITECTURE.md` para arquitectura completa
- Ver `static/js/README.md` para JavaScript
- Ver `static/css/README.md` para CSS

