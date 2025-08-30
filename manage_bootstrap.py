# manage_bootstrap.py
from pathlib import Path
from app import create_app, db

# Try Alembic upgrade if migrations/ exists; otherwise create all tables.
def main():
    app = create_app()
    with app.app_context():
        if Path("migrations").exists():
            try:
                from flask_migrate import upgrade
                upgrade()
                print("Alembic migrations applied.")
            except Exception as e:
                print("Alembic upgrade failed:", e)
                raise
        else:
            print("No migrations/ found; creating tables via db.create_all() ...")
            db.create_all()
            print("Tables created.")

if __name__ == "__main__":
    main()
mana
