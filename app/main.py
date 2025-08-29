# app/main.py

import base64
import io
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import db, Dataset, Analysis, Chart
from .analysis import run_basic_eda

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
@login_required
def dashboard():
    datasets = (
        Dataset.query
        .filter_by(user_id=current_user.id)
        .order_by(Dataset.uploaded_at.desc())
        .all()
    )
    return render_template("dashboard.html", datasets=datasets)

@main_bp.get("/upload")
@login_required
def upload_page():
    return render_template("upload.html")

@main_bp.post("/upload")
@login_required
def upload_post():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a CSV file.", "warning")
        return redirect(url_for("main.upload_page"))
    if not file.filename.lower().endswith(".csv"):
        flash("Only .csv files are allowed.", "danger")
        return redirect(url_for("main.upload_page"))

    data = file.read()
    if not data:
        flash("Uploaded file is empty.", "danger")
        return redirect(url_for("main.upload_page"))

    # Save dataset record (store raw bytes so filesystem isn’t needed)
    ds = Dataset(
        user_id=current_user.id,
        filename=file.filename,
        original_name=file.filename,
        blob=data,
    )
    db.session.add(ds)
    db.session.commit()
    current_app.logger.info(
        "User %s uploaded %s (%d bytes)", current_user.id, file.filename, len(data)
    )

    # Process immediately (for small files). For bigger jobs, add a background queue later.
    try:
        # 1) Read CSV with encoding fallbacks
        try:
            df = pd.read_csv(io.BytesIO(data))  # try UTF-8/UTF-8-SIG
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(data), encoding="latin-1")  # cp1252 fallback
        except Exception:
            # last resort: permissive parser for odd delimiters/bad rows
            df = pd.read_csv(
                io.BytesIO(data),
                encoding="latin-1",
                on_bad_lines="skip",
                engine="python",
            )

        # 2) Run analysis
        analysis_summary, charts = run_basic_eda(df)

        # 3) Persist analysis + charts
        a = Analysis(dataset_id=ds.id, summary_json=analysis_summary)
        db.session.add(a)
        db.session.flush()  # get a.id

        for title, png_bytes in charts:
            db.session.add(Chart(analysis_id=a.id, title=title, image=png_bytes))

        db.session.commit()
        return redirect(url_for("main.analysis_detail", analysis_id=a.id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Analysis failed")
        flash(f"Analysis error: {e}", "danger")
        return redirect(url_for("main.upload_page"))

@main_bp.get("/analysis/<int:analysis_id>")
@login_required
def analysis_detail(analysis_id: int):
    a = Analysis.query.get_or_404(analysis_id)
    if a.dataset.owner.id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.dashboard"))

    images = []
    for c in a.charts:
        b64 = base64.b64encode(c.image).decode("utf-8")
        images.append({"title": c.title, "data": f"data:image/png;base64,{b64}"})
    return render_template("analysis_detail.html", a=a, images=images)
