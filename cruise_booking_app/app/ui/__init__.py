from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.ui.views import home, marketing, status

    app.register_blueprint(home.bp)
    app.register_blueprint(status.bp)
    app.register_blueprint(marketing.bp)

    return app
