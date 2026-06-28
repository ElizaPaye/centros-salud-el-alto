from functools import wraps
from flask import abort
from flask_login import current_user


def requiere_rol(*roles_permitidos):
    """Uso: @requiere_rol('Administrador', 'Gestor')"""

    def decorador(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.tiene_rol(*roles_permitidos):
                abort(403)
            return f(*args, **kwargs)

        return envoltura

    return decorador
