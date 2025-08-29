# app/__init__.py
import logging, os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"

def create_app():
    app = Flask(__name__)

    # Choose config by FLASK_ENV=production in Heroku
    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .auth import auth_bp
    from .main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # JSON logs to stdout (Heroku best practice)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e): return (render_template("404.html"), 404)

    @app.errorhandler(500)
    def server_error(e): return (render_template("500.html"), 500)

    return app

# Flask-Login loader
from .models import User  # noqa: E402
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
