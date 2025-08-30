# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.types import JSON
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # NEW: Supabase user UUID (as string). Kept nullable to support legacy/local users.
    supabase_id = db.Column(db.String(36), unique=True, index=True, nullable=True)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # CHANGED: nullable=True because Supabase manages credentials.
    password_hash = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, server_default=func.now())

    datasets = db.relationship("Dataset", backref="owner", lazy=True)

    # Helpers still work for legacy/local-password users
    def set_password(self, pw: str) -> None:
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        # If we don't have a local hash (Supabase user), always return False here.
        # Authentication should be handled by Supabase before calling this.
        return bool(self.password_hash) and check_password_hash(self.password_hash, pw)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} supabase_id={self.supabase_id}>"


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    blob = db.Column(db.LargeBinary, nullable=False)  # store CSV bytes

    analyses = db.relationship("Analysis", backref="dataset", lazy=True)

    def __repr__(self) -> str:
        return f"<Dataset id={self.id} user_id={self.user_id} filename={self.filename}>"


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    summary_json = db.Column(JSON, nullable=False)  # works on SQLite & Postgres

    charts = db.relationship("Chart", backref="analysis", lazy=True)

    def __repr__(self) -> str:
        return f"<Analysis id={self.id} dataset_id={self.dataset_id}>"


class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)  # PNG bytes

    def __repr__(self) -> str:
        return f"<Chart id={self.id} analysis_id={self.analysis_id} title={self.title}>"
