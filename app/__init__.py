from datetime import timedelta
import os
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    
    # Imports inside to avoid circular references
    from .config import SECRET_KEY, UPLOAD_FOLDER, SESSION_LIFETIME_DAYS
    
    app.secret_key = SECRET_KEY
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.permanent_session_lifetime = timedelta(days=SESSION_LIFETIME_DAYS)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Blueprints registration
    from .auth import auth_bp
    from .api import api_bp
    from .routes import routes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(routes_bp)
    
    return app

def init_db_on_startup():
    from .db import init_database
    init_database()
