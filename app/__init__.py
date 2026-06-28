from flask import Flask

from config import config_by_name
from app.extensions import db, login_manager, migrate, bcrypt


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Importar modelos para que Flask-Migrate los detecte
    from app import models  # noqa

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))

    # Registrar blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.centros import centros_bp
    from app.blueprints.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(centros_bp)
    app.register_blueprint(main_bp)

    from app.cli import registrar_comandos
    registrar_comandos(app)

    return app
