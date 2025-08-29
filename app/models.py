# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.types import JSON
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    datasets = db.relationship("Dataset", backref="owner", lazy=True)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    blob = db.Column(db.LargeBinary, nullable=False)  # store CSV bytes

    analyses = db.relationship("Analysis", backref="dataset", lazy=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    summary_json = db.Column(JSON, nullable=False)  # works on SQLite & Postgres

    charts = db.relationship("Chart", backref="analysis", lazy=True)

class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)  # PNG bytes
