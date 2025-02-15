def init_routes(app):
    from .auth_routes import AuthRoutes
    from .admin_routes import AdminRoutes
    from .curso_routes import CursoRoutes
    AuthRoutes(app)
    AdminRoutes(app)
    CursoRoutes(app)
