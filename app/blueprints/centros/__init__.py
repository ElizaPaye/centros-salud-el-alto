from flask import Blueprint

centros_bp = Blueprint("centros", __name__, url_prefix="/centros")

from app.blueprints.centros import routes  # noqa
