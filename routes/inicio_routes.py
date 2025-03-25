from flask import redirect, url_for


class MainRoutes:
    def __init__(self, app):
        self.app = app
        self.init_routes()

    def init_routes(self):
        @self.app.route('/')
        def index():
            return redirect(url_for('dashboard'))
