def init_routes(app):
    from .auth_routes import AuthRoutes
    from .admin_routes import AdminRoutes
    from .curso_routes import CursoRoutes
    from .error_routes import ErrorRoutes
    from .inicio_routes import MainRoutes
    AuthRoutes(app)
    AdminRoutes(app)
    CursoRoutes(app)
    ErrorRoutes(app)
    MainRoutes(app)
