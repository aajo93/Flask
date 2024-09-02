from flask import Flask
from app import create_app, db
#models need to be imported before calling DB
from app.models.models import Test

application = create_app()

with application.app_context():
    db.create_all()

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0")
