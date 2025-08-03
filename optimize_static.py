#!/usr/bin/env python3
"""
Script para optimizar archivos estáticos para producción
"""

import os
import shutil
import gzip
from pathlib import Path

def compress_static_files():
    """Comprimir archivos CSS y JS para mejorar performance"""
    
    static_dir = Path('static')
    
    # Tipos de archivos a comprimir
    file_types = ['*.css', '*.js', '*.json']
    
    compressed_count = 0
    
    for file_type in file_types:
        for file_path in static_dir.rglob(file_type):
            if file_path.suffix in ['.css', '.js', '.json']:
                # Crear versión comprimida con gzip
                compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
                
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                print(f"Compressed: {file_path} -> {compressed_path}")
                compressed_count += 1
    
    print(f"\n✅ Compressed {compressed_count} files successfully!")

def minify_css():
    """Minificación básica de CSS (eliminar espacios extra y comentarios)"""
    
    css_files = list(Path('static/css').glob('*.css'))
    
    for css_file in css_files:
        if css_file.name.endswith('.min.css'):
            continue
            
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Minificación básica
        # Eliminar comentarios
        import re
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Eliminar espacios extra
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r';\s*}', '}', content)
        content = re.sub(r'{\s*', '{', content)
        content = re.sub(r';\s*', ';', content)
        content = content.strip()
        
        # Crear versión minificada
        min_file = css_file.with_suffix('.min.css')
        with open(min_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Minified: {css_file} -> {min_file}")

def optimize_images():
    """Optimizar imágenes (requiere Pillow)"""
    try:
        from PIL import Image
        import io
        
        image_dir = Path('static/img')
        if not image_dir.exists():
            print("No images directory found, skipping image optimization")
            return
            
        optimized_count = 0
        
        for img_path in image_dir.rglob('*'):
            if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    with Image.open(img_path) as img:
                        # Optimizar calidad para web
                        if img_path.suffix.lower() in ['.jpg', '.jpeg']:
                            img.save(img_path, format='JPEG', quality=85, optimize=True)
                        elif img_path.suffix.lower() == '.png':
                            img.save(img_path, format='PNG', optimize=True)
                        
                        optimized_count += 1
                        print(f"Optimized: {img_path}")
                        
                except Exception as e:
                    print(f"Error optimizing {img_path}: {e}")
        
        print(f"\n✅ Optimized {optimized_count} images successfully!")
        
    except ImportError:
        print("Pillow not installed, skipping image optimization")
        print("Install with: pip install Pillow")

def create_robots_txt():
    """Crear archivo robots.txt para SEO"""
    
    robots_content = """User-agent: *
Allow: /

# Disallow admin pages
Disallow: /admin
Disallow: /login
Disallow: /register

# Sitemap
Sitemap: https://tu-dominio.com/sitemap.xml
"""
    
    with open('static/robots.txt', 'w') as f:
        f.write(robots_content)
    
    print("✅ Created robots.txt")

def create_gitignore_production():
    """Crear .gitignore optimizado para producción"""
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Flask
instance/
.webassets-cache

# Environment files
.env
.env.local
.env.development
.env.production
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# Uploads (en producción estos van en volumen separado)
uploads/
static/uploads/

# Backups
*.sql
*.dump
backup/
backups/

# SSL certificates
*.pem
*.key
*.crt
ssl/

# Cache
.cache/
.npm/
node_modules/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Updated .gitignore for production")

def main():
    """Ejecutar todas las optimizaciones"""
    
    print("🚀 Optimizing static files for production...\n")
    
    # Crear directorios necesarios
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    
    # Ejecutar optimizaciones
    print("📦 Compressing static files...")
    compress_static_files()
    
    print("\n🎨 Minifying CSS...")
    minify_css()
    
    print("\n🖼️ Optimizing images...")
    optimize_images()
    
    print("\n🤖 Creating robots.txt...")
    create_robots_txt()
    
    print("\n📝 Updating .gitignore...")
    create_gitignore_production()
    
    print("\n✅ All optimizations completed!")
    print("\n📋 Next steps:")
    print("1. Test your application locally")
    print("2. Update template links to use .min.css files")
    print("3. Configure nginx to serve .gz files when available")
    print("4. Deploy to production")

if __name__ == "__main__":
    main()