# app/auth.py
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from .models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.get("/login")
def login_page():
    return render_template("auth_login.html")

@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    pw = request.form.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(pw):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.login_page"))
    login_user(user)
    return redirect(url_for("main.dashboard"))

@auth_bp.get("/register")
def register_page():
    return render_template("auth_register.html")

@auth_bp.post("/register")
def register_post():
    email = request.form.get("email", "").strip().lower()
    pw = request.form.get("password", "")
    if not email or not pw:
        flash("Email and password are required.", "warning")
        return redirect(url_for("auth.register_page"))
    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "warning")
        return redirect(url_for("auth.register_page"))
    user = User(email=email)
    user.set_password(pw)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("main.dashboard"))

@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))
