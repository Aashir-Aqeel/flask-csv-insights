# app/__init__.py
import logging
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from supabase import create_client  # pip install supabase
from .config import DevelopmentConfig, ProductionConfig

# Flask extensions (global singletons)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login_page"


def _init_supabase(app: Flask) -> None:
    """
    Create and attach a Supabase client to the app (app.extensions['supabase']).
    Reads SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE) from env.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")
    if url and key:
        app.extensions["supabase"] = create_client(url, key)
        app.logger.info("Supabase client initialized.")
    else:
        app.logger.warning(
            "Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY "
            "(or SUPABASE_SERVICE_ROLE) in environment variables."
        )


def create_app():
    app = Flask(__name__)

    # Select config via FLASK_ENV
    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
        # Sensible cookie security defaults for production
        app.config.setdefault("SESSION_COOKIE_SECURE", True)
        app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Supabase client (for auth integration)
    _init_supabase(app)

    # Register blueprints
    from .auth import auth_bp
    from .main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # JSON-ish logs to stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled server error: %s", e)
        return render_template("500.html"), 500

    return app


# Flask-Login loader
from .models import User  # noqa: E402


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
