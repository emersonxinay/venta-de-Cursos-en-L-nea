def init_routes(app):
    from .auth_routes import AuthRoutes
    from .admin_routes import AdminRoutes
    AuthRoutes(app)
    AdminRoutes(app)
