from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'

    from app.ui.views import home, status, marketing
    
    app.register_blueprint(home.bp)
    app.register_blueprint(status.bp)
    app.register_blueprint(marketing.bp)

    return app
