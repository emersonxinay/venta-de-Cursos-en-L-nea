from flask import render_template


class ErrorRoutes:
    def __init__(self, app):
        self.app = app
        self.init_routes()

    def init_routes(self):
        @self.app.errorhandler(404)
        def error_404(e):
            return render_template('404.html'), 404
