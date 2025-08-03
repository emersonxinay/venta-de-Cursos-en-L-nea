from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os


class CursoRoutes:
    def __init__(self, app):
        self.app = app
        from app import flask_app, db, Curso, Seccion, Venta, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
        self.flask_app = flask_app
        self.db = db
        self.Curso = Curso
        self.Seccion = Seccion
        self.Venta = Venta
        self.UPLOAD_FOLDER = UPLOAD_FOLDER
        self.ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
        self.init_routes()

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def init_routes(self):
        @self.app.route('/curso/<int:curso_id>')
        def ver_curso(curso_id):
            with self.flask_app.app_context():
                curso = self.Curso.query.get_or_404(curso_id)
                secciones = self.Seccion.query.filter_by(
                    curso_id=curso_id).order_by(self.Seccion.id).all()
                
                venta_confirmada = None
                venta_pendiente = None
                
                # Solo buscar ventas si el usuario está autenticado
                if current_user.is_authenticated:
                    # Buscar venta confirmada
                    venta_confirmada = self.Venta.query.filter_by(
                        usuario_id=current_user.id, 
                        curso_id=curso_id, 
                        estado_transferencia='confirmada'
                    ).first()
                    
                    # Buscar venta pendiente
                    venta_pendiente = self.Venta.query.filter_by(
                        usuario_id=current_user.id, 
                        curso_id=curso_id, 
                        estado_transferencia='pendiente'
                    ).first()
                
                # Determinar qué secciones son accesibles
                # 1. Si es admin, puede ver todo
                # 2. Si tiene venta confirmada, puede ver todo  
                # 3. TODOS (incluso sin login) pueden ver las primeras 2 lecciones completas
                # 4. Si tiene transferencia pendiente, igual solo ve preview (primeras 2)
                
                # IMPORTANTE: Solo check authenticated después de verificar que current_user existe
                es_admin = current_user.is_authenticated and hasattr(current_user, 'rol') and current_user.rol == 'admin'
                tiene_venta_confirmada = venta_confirmada is not None
                
                tiene_acceso_completo = es_admin or tiene_venta_confirmada
                
                # CAMBIO IMPORTANTE: Las primeras 2 secciones son SIEMPRE accesibles para TODOS
                MAX_PREVIEW_SECTIONS = 2
                
                for i, seccion in enumerate(secciones):
                    if i < MAX_PREVIEW_SECTIONS:
                        # Las primeras 2 son SIEMPRE accesibles para TODOS
                        seccion.es_preview_gratis = True
                        seccion.es_accesible = True
                        seccion.es_bloqueado = False
                    else:
                        # Las demás solo accesibles si tiene acceso completo
                        seccion.es_preview_gratis = False
                        seccion.es_accesible = tiene_acceso_completo
                        seccion.es_bloqueado = not tiene_acceso_completo
                
                return render_template(
                    'ver_curso.html', 
                    curso=curso, 
                    secciones=secciones, 
                    venta=venta_confirmada,
                    venta_pendiente=venta_pendiente,
                    tiene_acceso_completo=tiene_acceso_completo,
                    max_preview_sections=MAX_PREVIEW_SECTIONS
                )

        @self.app.route('/curso/<int:curso_id>/seccion/nueva', methods=['GET', 'POST'])
        @login_required
        def nueva_seccion(curso_id):
            with self.flask_app.app_context():
                curso = self.Curso.query.get_or_404(curso_id)
                if request.method == 'POST':
                    titulo = request.form['titulo']
                    descripcion = request.form['descripcion']
                    video_url = request.form['video_url']
                    es_gratis = 'es_gratis' in request.form
                    video_file = None
                    if 'video_file' in request.files:
                        file = request.files['video_file']
                        if file and self.allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(
                                self.UPLOAD_FOLDER, filename))
                            video_file = os.path.join(
                                self.UPLOAD_FOLDER, filename)

                    seccion = self.Seccion(titulo=titulo, descripcion=descripcion,
                                           video_url=video_url, curso_id=curso.id, es_gratis=es_gratis, video_file=video_file)
                    self.db.session.add(seccion)
                    self.db.session.commit()
                    flash('Sección creada exitosamente.')
                    return redirect(url_for('ver_curso', curso_id=curso.id))
                return render_template('nueva_seccion.html', curso=curso)

        @self.app.route('/curso/<int:curso_id>/seccion/<int:seccion_id>/editar', methods=['GET', 'POST'])
        @login_required
        def editar_seccion(curso_id, seccion_id):
            with self.flask_app.app_context():
                seccion = self.Seccion.query.get_or_404(seccion_id)
                if request.method == 'POST':
                    seccion.titulo = request.form['titulo']
                    seccion.descripcion = request.form['descripcion']
                    seccion.video_url = request.form['video_url']
                    seccion.es_gratis = 'es_gratis' in request.form
                    if 'video_file' in request.files:
                        file = request.files['video_file']
                        if file and self.allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join(
                                self.UPLOAD_FOLDER, filename))
                            seccion.video_file = os.path.join(
                                self.UPLOAD_FOLDER, filename)

                    self.db.session.commit()
                    flash('Sección actualizada exitosamente.')
                    return redirect(url_for('ver_curso', curso_id=curso_id))
                return render_template('editar_seccion.html', seccion=seccion)

        @self.app.route('/curso/<int:curso_id>/seccion/<int:seccion_id>/eliminar', methods=['POST'])
        @login_required
        def eliminar_seccion(curso_id, seccion_id):
            with self.flask_app.app_context():
                seccion = self.Seccion.query.get_or_404(seccion_id)
                self.db.session.delete(seccion)
                self.db.session.commit()
                flash('Sección eliminada exitosamente.')
                return redirect(url_for('ver_curso', curso_id=curso_id))

        @self.app.route('/nuevo_curso', methods=['GET', 'POST'])
        @login_required
        def nuevo_curso():
            with self.flask_app.app_context():
                if current_user.rol != 'admin':
                    return redirect(url_for('dashboard'))
                if request.method == 'POST':
                    nuevo_curso = self.Curso(
                        nombre=request.form['nombre'],
                        descripcion=request.form['descripcion'],
                        precio=float(request.form['precio'])
                    )
                    self.db.session.add(nuevo_curso)
                    self.db.session.commit()
                    flash('Curso creado exitosamente.')
                    return redirect(url_for('dashboard'))
                return render_template('nuevo_curso.html')

        @self.app.route('/editar_curso/<int:curso_id>', methods=['GET', 'POST'])
        @login_required
        def editar_curso(curso_id):
            with self.flask_app.app_context():
                if current_user.rol != 'admin':
                    return redirect(url_for('dashboard'))
                curso = self.Curso.query.get_or_404(curso_id)
                if request.method == 'POST':
                    curso.nombre = request.form['nombre']
                    curso.descripcion = request.form['descripcion']
                    curso.precio = float(request.form['precio'])
                    self.db.session.commit()
                    flash('Curso actualizado exitosamente.')
                    return redirect(url_for('admin_dashboard'))
                return render_template('editar_curso.html', curso=curso)

        @self.app.route('/eliminar_curso/<int:curso_id>', methods=['POST'])
        @login_required
        def eliminar_curso(curso_id):
            with self.flask_app.app_context():
                if current_user.rol != 'admin':
                    return redirect(url_for('dashboard'))
                curso = self.Curso.query.get_or_404(curso_id)
                self.db.session.delete(curso)
                self.db.session.commit()
                flash('Curso eliminado exitosamente.')
                return redirect(url_for('admin_dashboard'))
