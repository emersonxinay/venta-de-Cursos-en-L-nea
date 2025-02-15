from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta


class AdminRoutes:
    def __init__(self, app):
        self.app = app
        from app import flask_app, db, Usuario, Curso, Venta
        self.flask_app = flask_app
        self.db = db
        self.Usuario = Usuario
        self.Curso = Curso
        self.Venta = Venta
        self.init_routes()

    def init_routes(self):
        @self.app.route('/admin_dashboard')
        @login_required
        def admin_dashboard():
            with self.flask_app.app_context():
                if current_user.rol != 'admin':
                    return redirect(url_for('dashboard'))

                # Obtener las ventas confirmadas del día, semana, mes y año
                hoy = datetime.utcnow().date()
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                inicio_mes = hoy.replace(day=1)
                inicio_ano = hoy.replace(month=1, day=1)

                ventas_dia = self.Venta.query.filter(self.db.func.date(
                    self.Venta.fecha_venta) == hoy, self.Venta.estado_transferencia == 'confirmada').all()
                ventas_semana = self.Venta.query.filter(self.db.func.date(
                    self.Venta.fecha_venta) >= inicio_semana, self.Venta.estado_transferencia == 'confirmada').all()
                ventas_mes = self.Venta.query.filter(self.db.func.date(
                    self.Venta.fecha_venta) >= inicio_mes, self.Venta.estado_transferencia == 'confirmada').all()
                ventas_ano = self.Venta.query.filter(self.db.func.date(
                    self.Venta.fecha_venta) >= inicio_ano, self.Venta.estado_transferencia == 'confirmada').all()

                # Calcular el total de ventas confirmadas
                total_dia = sum(venta.curso.precio for venta in ventas_dia)
                total_semana = sum(
                    venta.curso.precio for venta in ventas_semana)
                total_mes = sum(venta.curso.precio for venta in ventas_mes)
                total_ano = sum(venta.curso.precio for venta in ventas_ano)

                # Obtener los cursos más vendidos
                cursos_mas_vendidos = self.db.session.query(
                    self.Curso.nombre, self.db.func.count(
                        self.Venta.id).label('total_ventas')
                ).join(self.Venta).filter(self.Venta.estado_transferencia == 'confirmada').group_by(self.Curso.id).order_by(self.db.func.count(self.Venta.id).desc()).all()

                # Obtener las devoluciones
                devoluciones = self.db.session.query(
                    self.Curso.nombre, self.db.func.count(
                        self.Venta.id).label('total_devoluciones')
                ).join(self.Venta).filter(self.Venta.estado_transferencia == 'devuelta').group_by(self.Curso.id).order_by(self.db.func.count(self.Venta.id).desc()).all()

                # Calcular el total de devoluciones
                total_devoluciones = sum(venta.curso.precio for venta in self.Venta.query.filter_by(
                    estado_transferencia='devuelta').all())

                # Calcular las ventas netas
                ventas_netas_dia = total_dia - sum(venta.curso.precio for venta in self.Venta.query.filter(
                    self.db.func.date(self.Venta.fecha_venta) == hoy, self.Venta.estado_transferencia == 'devuelta').all())
                ventas_netas_semana = total_semana - sum(venta.curso.precio for venta in self.Venta.query.filter(
                    self.db.func.date(self.Venta.fecha_venta) >= inicio_semana, self.Venta.estado_transferencia == 'devuelta').all())
                ventas_netas_mes = total_mes - sum(venta.curso.precio for venta in self.Venta.query.filter(
                    self.db.func.date(self.Venta.fecha_venta) >= inicio_mes, self.Venta.estado_transferencia == 'devuelta').all())
                ventas_netas_ano = total_ano - sum(venta.curso.precio for venta in self.Venta.query.filter(
                    self.db.func.date(self.Venta.fecha_venta) >= inicio_ano, self.Venta.estado_transferencia == 'devuelta').all())

                # Obtener todas las ventas para la gestión de accesos
                ventas = self.Venta.query.all()
                # Obtener todos los usuarios
                usuarios = self.Usuario.query.all()

                # Obtener todos los cursos
                cursos = self.Curso.query.all()

                # Obtener las transferencias pendientes
                transferencias = self.Venta.query.filter_by(
                    metodo_pago='transferencia', estado_transferencia='pendiente').all()

                return render_template('admin_dashboard.html',
                                       total_dia=total_dia,
                                       total_semana=total_semana,
                                       total_mes=total_mes,
                                       total_ano=total_ano,
                                       cursos_mas_vendidos=cursos_mas_vendidos,
                                       devoluciones=devoluciones,
                                       total_devoluciones=total_devoluciones,
                                       ventas_netas_dia=ventas_netas_dia,
                                       ventas_netas_semana=ventas_netas_semana,
                                       ventas_netas_mes=ventas_netas_mes,
                                       ventas_netas_ano=ventas_netas_ano,
                                       ventas=ventas,
                                       usuarios=usuarios,
                                       cursos=cursos,
                                       transferencias=transferencias)
