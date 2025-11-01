# Sistema Modular de CSS - CompilandoCode

## 📁 Estructura de Archivos CSS

```
static/css/
├── app.css                      # 🎯 PUNTO DE ENTRADA PRINCIPAL
│
├── base/                        # Variables y configuración base
│   ├── main.css                # Variables CSS y base styles
│   └── design-system.css       # Sistema de diseño y tokens
│
├── utilities/                   # Utilidades reutilizables
│   └── animations.css          # Animaciones y transitions
│
├── components/                  # Componentes UI reutilizables
│   ├── components.css          # Componentes generales
│   └── modern-ui.css           # Componentes modernos con degradados
│
├── pages/                       # Estilos específicos por página
│   ├── auth.css                # Páginas de autenticación
│   ├── styles_login.css        # Login específico
│   ├── styles_dashboard.css    # Dashboard principal
│   ├── styles_admin_dashboard.css # Panel de administración
│   ├── styles_ver_curso.css    # Vista de curso
│   └── styles_comprar_curso.css # Proceso de compra
│
└── layout/                      # Layout y estructura
    ├── styles_navbar.css        # Navegación
    └── styles_footer.css        # Footer
```

## 🚀 Uso

### Opción 1: Importar TODO (Recomendado para producción)

En `base.html`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

Esto carga **todos** los estilos en el orden correcto.

### Opción 2: Importar Solo lo Necesario (Para desarrollo)

Si quieres optimizar y solo cargar lo necesario en cada página:

```html
<!-- Base (siempre necesario) -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/design-system.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/modern-ui.css') }}">

<!-- Página específica -->
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles_dashboard.css') }}">
{% endblock %}
```

## 🎨 Sistema de Diseño

### Variables CSS Disponibles

```css
/* Colores principales */
--color-primary: #6366f1;
--color-secondary: #8b5cf6;
--color-success: #10b981;
--color-warning: #f59e0b;
--color-danger: #ef4444;
--color-info: #3b82f6;

/* Degradados */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-blue-purple: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
--gradient-purple-pink: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
--gradient-orange-amber: linear-gradient(135deg, #fb923c 0%, #f59e0b 100%);
--gradient-emerald-teal: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
--gradient-slate-blue: linear-gradient(135deg, #64748b 0%, #3b82f6 100%);

/* Espaciado */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;

/* Bordes */
--radius-sm: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
--radius-2xl: 1.5rem;
--radius-full: 9999px;

/* Sombras */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Tipografía */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'Fira Code', 'Courier New', monospace;
```

### Clases Utilitarias

```css
/* Cards */
.card { /* Card básica */ }
.gradient-card { /* Card con degradado */ }
.glass-effect { /* Efecto glassmorphism */ }

/* Botones */
.btn-gradient { /* Botón con degradado */ }
.btn-ghost-gradient { /* Botón outline con degradado */ }
.btn-sm, .btn-md, .btn-lg { /* Tamaños */ }

/* Badges */
.badge-gradient { /* Badge con degradado */ }
.badge-gradient.success { /* Badge verde */ }
.badge-gradient.warning { /* Badge amarillo */ }
.badge-gradient.danger { /* Badge rojo */ }

/* Progress */
.progress-bar { /* Barra de progreso */ }
.progress-fill { /* Relleno de progreso */ }

/* Animaciones */
.animate-fadeIn { /* Fade in */ }
.animate-fadeInUp { /* Fade in desde abajo */ }
.hover-lift { /* Efecto hover levanta */ }
.card-animated { /* Card con animación */ }

/* Layout */
.container-fluid { /* Container fluido */ }
.flex { /* Flexbox */ }
.grid { /* Grid */ }
```

## 📐 Mobile-First Approach

Todos los estilos están diseñados con enfoque mobile-first:

```css
/* Base: Mobile (< 640px) */
.stats-grid {
  grid-template-columns: 1fr;
}

/* Tablet: sm (≥ 640px) */
@media (min-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: md (≥ 768px) */
@media (min-width: 768px) {
  /* ... */
}

/* Large Desktop: lg (≥ 1024px) */
@media (min-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Extra Large: xl (≥ 1280px) */
@media (min-width: 1280px) {
  /* ... */
}
```

## 🎯 Breakpoints

```css
/* xs: < 640px   - Mobile */
/* sm: ≥ 640px   - Large mobile / Small tablet */
/* md: ≥ 768px   - Tablet */
/* lg: ≥ 1024px  - Desktop */
/* xl: ≥ 1280px  - Large desktop */
/* 2xl: ≥ 1536px - Extra large desktop */
```

## 🌓 Dark Mode

El sistema usa variables CSS para soportar dark mode:

```css
/* Light mode (default) */
:root {
  --bg-primary: #ffffff;
  --text-primary: #1f2937;
}

/* Dark mode */
:root[data-theme="dark"] {
  --bg-primary: #1a1a2e;
  --text-primary: #f9fafb;
}
```

Cambiar tema:

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

## 🎨 Crear Nuevos Componentes CSS

### 1. Crear archivo en carpeta apropiada

```bash
# Para componente nuevo
touch static/css/components/mi-componente.css

# Para página nueva
touch static/css/pages/mi-pagina.css
```

### 2. Agregar estilos usando variables

```css
/* components/mi-componente.css */
.mi-componente {
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.mi-componente:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}
```

### 3. Importar en app.css

```css
/* En app.css, sección COMPONENTS */
@import url('./components/mi-componente.css');
```

## 🔧 Optimización

### Para Desarrollo

Usa `app.css` que importa todo:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

### Para Producción

Opción 1: Minificar todo con PostCSS/cssnano

```bash
npm install -g cssnano postcss-cli
postcss static/css/app.css -o static/css/dist/app.min.css --use cssnano
```

Opción 2: Cargar solo lo necesario por página

```html
<!-- base.html -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/design-system.css') }}">

<!-- dashboard.html -->
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles_dashboard.css') }}">
{% endblock %}
```

## ♿ Accesibilidad

El sistema incluye:

✅ **Focus visible** para navegación por teclado
✅ **Reduced motion** para usuarios sensibles a animaciones
✅ **High contrast** para mejor visibilidad
✅ **Color contrast** ratios AAA
✅ **Print styles** optimizados

## 🐛 Debug

### Ver variables CSS activas:

```javascript
// En consola del navegador
const root = document.documentElement;
const styles = getComputedStyle(root);

console.log('Primary color:', styles.getPropertyValue('--color-primary'));
console.log('Background:', styles.getPropertyValue('--bg-primary'));
```

### Inspeccionar cascade:

```javascript
// Ver todos los estilos aplicados
const element = document.querySelector('.mi-elemento');
console.log(getComputedStyle(element));
```

## 📦 Build Pipeline (Futuro)

```bash
# Instalar herramientas
npm install -D postcss autoprefixer cssnano

# postcss.config.js
module.exports = {
  plugins: [
    require('autoprefixer'),
    require('cssnano')({
      preset: 'default'
    })
  ]
};

# Build
npx postcss static/css/app.css -o static/css/dist/app.min.css
```

## 🎓 Convenciones

1. **Nombres de clases**: usar kebab-case (`.mi-clase`)
2. **Variables CSS**: prefijo con `--` (` --mi-variable`)
3. **BEM opcional**: para componentes complejos (`.block__element--modifier`)
4. **Mobile-first**: siempre empezar con estilos mobile
5. **Variables primero**: usar variables del design system
6. **Comentarios**: documentar secciones complejas

## 🔄 Migración de Inline Styles

### Antes:

```html
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem;">
  Contenido
</div>
```

### Después:

```html
<div class="gradient-card">
  <div class="gradient-card-body">
    Contenido
  </div>
</div>
```

## 📚 Referencias

- [MDN CSS Reference](https://developer.mozilla.org/es/docs/Web/CSS)
- [CSS Variables](https://developer.mozilla.org/es/docs/Web/CSS/Using_CSS_custom_properties)
- [CSS Grid](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
