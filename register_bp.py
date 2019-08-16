from views.response import response_bp
from views.upload_api import upload_bp


def register_bp(app):
    app.register_blueprint(response_bp, url_prefix='/api/v1.0.0')
    app.register_blueprint(upload_bp, url_prefix='/api/v1.0.0')
