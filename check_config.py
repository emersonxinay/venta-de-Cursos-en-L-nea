#!/usr/bin/env python3
"""
Script para verificar la configuración de producción
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

def check_environment():
    """Verificar variables de entorno críticas"""
    print("🔍 Verificando configuración de entorno...\n")
    
    # Cargar variables de entorno
    load_dotenv()
    
    critical_vars = {
        'DATABASE_URL': 'URL de base de datos',
        'SECRET_KEY': 'Clave secreta de Flask'
    }
    
    missing_vars = []
    
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"❌ {var} - {description}")
            print(f"❌ {var} - {description} - NO CONFIGURADO")
        else:
            # Mostrar solo los primeros caracteres por seguridad
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var} - {description} - CONFIGURADO ({masked_value})")
    
    if missing_vars:
        print(f"\n⚠️  Variables críticas faltantes: {len(missing_vars)}")
        return False
    
    print("\n✅ Todas las variables críticas están configuradas")
    return True

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("\n🔍 Verificando conexión a base de datos...\n")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no está configurado")
        return False
    
    try:
        # Parsear la URL de la base de datos
        parsed = urlparse(database_url)
        
        print(f"📊 Intentando conectar a:")
        print(f"   Host: {parsed.hostname}")
        print(f"   Puerto: {parsed.port}")
        print(f"   Base de datos: {parsed.path[1:]}")  # Remover el '/' inicial
        print(f"   Usuario: {parsed.username}")
        
        # Intentar conexión
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar que la base de datos tenga el nombre correcto
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        
        if db_name != 'db_venta_cursos':
            print(f"⚠️  La base de datos actual es '{db_name}', esperaba 'db_venta_cursos'")
            print("   Esto puede estar bien si usas un nombre diferente en producción")
        
        # Verificar algunas tablas principales
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('usuario', 'curso', 'seccion', 'venta')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        expected_tables = ['curso', 'seccion', 'usuario', 'venta']
        found_tables = [table[0] for table in tables]
        
        print(f"\n📋 Tablas encontradas: {found_tables}")
        
        missing_tables = [table for table in expected_tables if table not in found_tables]
        if missing_tables:
            print(f"⚠️  Tablas faltantes: {missing_tables}")
            print("   Ejecuta las migraciones: flask db upgrade")
        else:
            print("✅ Todas las tablas principales están presentes")
        
        cursor.close()
        conn.close()
        print("✅ Conexión a base de datos exitosa")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_flask_config():
    """Verificar configuración de Flask"""
    print("\n🔍 Verificando configuración de Flask...\n")
    
    flask_env = os.getenv('FLASK_ENV', 'development')
    flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    print(f"🌍 FLASK_ENV: {flask_env}")
    print(f"🐛 FLASK_DEBUG: {flask_debug}")
    
    if flask_env == 'production':
        if flask_debug:
            print("⚠️  DEBUG está activado en producción - DESACTIVARLO")
            return False
        else:
            print("✅ Configuración de producción correcta")
    else:
        print("ℹ️  Modo de desarrollo detectado")
    
    return True

def check_payment_services():
    """Verificar configuración de servicios de pago"""
    print("\n🔍 Verificando servicios de pago...\n")
    
    # Verificar Stripe
    stripe_live = os.getenv('STRIPE_API_KEY_LIVE')
    stripe_pub_live = os.getenv('STRIPE_PUBLISHABLE_KEY_LIVE')
    
    if stripe_live and stripe_pub_live:
        print("✅ Stripe (Producción) - Configurado")
    else:
        print("ℹ️  Stripe (Producción) - No configurado (opcional)")
    
    # Verificar PayPal
    paypal_live_id = os.getenv('PAYPAL_CLIENT_ID_LIVE')
    paypal_live_secret = os.getenv('PAYPAL_CLIENT_SECRET_LIVE')
    
    if paypal_live_id and paypal_live_secret:
        print("✅ PayPal (Producción) - Configurado")
    else:
        print("ℹ️  PayPal (Producción) - No configurado (opcional)")
    
    return True

def generate_secret_key():
    """Generar una clave secreta segura"""
    import secrets
    return secrets.token_urlsafe(32)

def main():
    """Ejecutar todas las verificaciones"""
    print("🚀 VERIFICADOR DE CONFIGURACIÓN PARA PRODUCCIÓN")
    print("=" * 50)
    
    all_good = True
    
    # Verificar entorno
    if not check_environment():
        all_good = False
    
    # Verificar Flask
    if not check_flask_config():
        all_good = False
    
    # Verificar base de datos
    if not check_database_connection():
        all_good = False
    
    # Verificar pagos
    check_payment_services()
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 ¡Configuración lista para producción!")
        print("\n📋 Pasos siguientes:")
        print("1. Ejecutar migraciones: flask db upgrade")
        print("2. Crear usuario admin inicial")
        print("3. Probar la aplicación localmente")
        print("4. Desplegar en Digital Ocean")
    else:
        print("❌ Hay problemas en la configuración")
        print("\n🔧 Acciones requeridas:")
        print("1. Revisar archivo .env")
        print("2. Configurar variables faltantes")
        print("3. Verificar conexión a base de datos")
        
        if not os.getenv('SECRET_KEY'):
            print(f"\n🔑 Clave secreta sugerida para SECRET_KEY:")
            print(f"SECRET_KEY={generate_secret_key()}")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())