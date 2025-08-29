# app/config.py
import os

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB uploads

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

class ProductionConfig(BaseConfig):
    # Heroku provides DATABASE_URL; ensure correct scheme for SQLAlchemy
    raw = os.environ.get("DATABASE_URL")
    if raw and raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = raw or "sqlite:///prod.db"
