def init_routes(app):
    from .auth_routes import AuthRoutes
    AuthRoutes(app)
