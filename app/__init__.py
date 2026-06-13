from datetime import datetime, timezone
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.utils import setup_logging, register_error_handlers
    setup_logging(app)
    register_error_handlers(app)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.tasks import tasks_bp
    from app.routes.projects import projects_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(ai_bp, url_prefix="/ai")

    @app.context_processor
    def inject_now():
        return {"now": datetime.now(timezone.utc).replace(tzinfo=None)}

    with app.app_context():
        from app import models
        db.create_all()

    return app
