import os
from dotenv import load_dotenv

# Cargar variables de entorno
project_home = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(project_home, '.env'))

# Importar la app y funciones de inicialización
from app import app, init_app, db

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# Inicializar la app siempre (Gunicorn la necesita)
init_app()

# Configuración de logs para producción
if __name__ != "__main__":
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            'logs/app.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CompilandoCode startup')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

