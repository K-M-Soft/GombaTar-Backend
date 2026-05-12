import os
from flask import Flask

from app.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config['DATABASE_URL'] = os.environ.get("DATABASE_URL")

    app.register_blueprint(api_bp)

    return app