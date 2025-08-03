#!/usr/bin/env python3
"""
Script para probar la aplicación localmente con configuración de producción
"""

import os
import sys
import shutil
from dotenv import load_dotenv

def setup_production_testing():
    """Configurar entorno para testing local con BD de producción"""
    
    print("🔧 Configurando testing local con base de datos de producción...\n")
    
    # 1. Verificar que existe el archivo de configuración
    config_file = ".env.local.production"
    if not os.path.exists(config_file):
        print(f"❌ No se encontró {config_file}")
        print("Crea el archivo con la configuración de tu base de datos de Digital Ocean")
        return False
    
    # 2. Hacer backup del .env actual si existe
    if os.path.exists(".env"):
        backup_name = ".env.backup"
        shutil.copy2(".env", backup_name)
        print(f"📋 Backup creado: {backup_name}")
    
    # 3. Copiar configuración de testing
    shutil.copy2(config_file, ".env")
    print(f"✅ Configuración copiada de {config_file} a .env")
    
    # 4. Cargar y verificar variables
    load_dotenv()
    
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        print("Edita .env.local.production con tus valores reales")
        return False
    
    print("✅ Variables de entorno configuradas")
    return True

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🔍 Probando conexión a base de datos...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.getenv('DATABASE_URL')
        parsed = urlparse(database_url)
        
        print(f"📊 Conectando a:")
        print(f"   Host: {parsed.hostname}")
        print(f"   Puerto: {parsed.port}")
        print(f"   Base de datos: {parsed.path[1:]}")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar algunas tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('usuario', 'curso', 'seccion', 'venta')
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tablas encontradas: {tables}")
        
        # Contar registros básicos
        cursor.execute("SELECT COUNT(*) FROM usuario")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM curso")
        courses_count = cursor.fetchone()[0]
        
        print(f"👥 Usuarios: {users_count}")
        print(f"📚 Cursos: {courses_count}")
        
        cursor.close()
        conn.close()
        
        print("✅ Conexión exitosa a base de datos de producción")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def start_app():
    """Iniciar la aplicación en modo testing"""
    print("\n🚀 Iniciando aplicación en modo testing local...")
    print("📍 URL: http://localhost:5000")
    print("🛑 Presiona Ctrl+C para detener")
    print("\n" + "="*50)
    
    # Importar y ejecutar app
    try:
        import app
        app.app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,  # Modo producción
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida")
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")

def restore_env():
    """Restaurar configuración original"""
    if os.path.exists(".env.backup"):
        shutil.copy2(".env.backup", ".env")
        os.remove(".env.backup")
        print("✅ Configuración original restaurada")
    else:
        if os.path.exists(".env"):
            os.remove(".env")
        print("✅ Configuración de testing removida")

def main():
    """Función principal"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_env()
        return
    
    print("🧪 TESTING LOCAL CON BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 55)
    
    try:
        # 1. Configurar entorno
        if not setup_production_testing():
            return 1
        
        # 2. Probar conexión
        if not test_database_connection():
            print("\n❌ No se pudo conectar a la base de datos")
            print("Verifica la configuración en .env.local.production")
            return 1
        
        # 3. Iniciar aplicación
        start_app()
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrumpido")
    finally:
        # Restaurar configuración
        restore_env()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())