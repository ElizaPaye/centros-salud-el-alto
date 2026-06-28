from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func

from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models import (
    CentroSalud, Distrito, TipoCentro, Especialidad, Usuario, Rol, Comentario,
    CentroEspecialidad, CoberturaSanitaria,
)
from app.utils import requiere_rol


# Configuración del explorador de base de datos:
# cada entrada define que modelo mostrar, su etiqueta y que columnas exponer
# (deliberadamente se EXCLUYE password_hash por seguridad, aunque la tabla usuarios sí es visible)
TABLAS_BD = {
    "usuarios": {
        "modelo": Usuario, "etiqueta": "Usuarios", "icono": "bi-people-fill",
        "columnas": ["id", "nombre", "username", "rol", "distrito", "activo", "fecha_registro"],
    },
    "roles": {
        "modelo": Rol, "etiqueta": "Roles", "icono": "bi-shield-lock-fill",
        "columnas": ["id", "nombre"],
    },
    "distritos": {
        "modelo": Distrito, "etiqueta": "Distritos", "icono": "bi-geo-alt-fill",
        "columnas": ["id", "nombre", "poblacion_total", "superficie_km2"],
    },
    "tipos_centro": {
        "modelo": TipoCentro, "etiqueta": "Tipos de Centro", "icono": "bi-tags-fill",
        "columnas": ["id", "nombre"],
    },
    "centros_salud": {
        "modelo": CentroSalud, "etiqueta": "Centros de Salud", "icono": "bi-hospital-fill",
        "columnas": ["id", "nombre", "tipo_centro", "distrito", "direccion", "capacidad", "estado"],
    },
    "especialidades": {
        "modelo": Especialidad, "etiqueta": "Especialidades", "icono": "bi-clipboard2-pulse-fill",
        "columnas": ["id", "nombre", "descripcion"],
    },
    "centro_Especialidad": {
        "modelo": CentroEspecialidad, "etiqueta": "Centro-Especialidad (N:M)", "icono": "bi-diagram-3-fill",
        "columnas": ["id", "centro", "especialidad"],
    },
    "cobertura_sanitaria": {
        "modelo": CoberturaSanitaria, "etiqueta": "Cobertura Sanitaria", "icono": "bi-bar-chart-fill",
        "columnas": ["id", "distrito", "anio", "poblacion", "num_centros", "indice_cobertura"],
    },
    "comentarios": {
        "modelo": Comentario, "etiqueta": "Comentarios", "icono": "bi-chat-dots-fill",
        "columnas": ["id", "usuario", "centro", "calificacion", "comentario", "fecha"],
    },
}


def _valor_columna(registro, columna):
    """Obtiene el valor a mostrar para una columna, resolviendo relaciones (ej: rol -> rol.nombre)."""
    valor = getattr(registro, columna, None)
    if valor is None:
        return "-"
    if columna in ("rol", "distrito", "tipo_centro", "centro", "especialidad", "usuario"):
        return getattr(valor, "nombre", str(valor))
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return valor


@admin_bp.route("/base-datos")
@login_required
@requiere_rol("Administrador")
def base_datos():
    resumen = []
    for clave, info in TABLAS_BD.items():
        total = info["modelo"].query.count()
        resumen.append({"clave": clave, "etiqueta": info["etiqueta"], "icono": info["icono"], "total": total})
    return render_template("admin/base_datos.html", resumen=resumen)


@admin_bp.route("/base-datos/<tabla>")
@login_required
@requiere_rol("Administrador")
def ver_tabla(tabla):
    info = TABLAS_BD.get(tabla)
    if not info:
        flash("Tabla no encontrada.", "danger")
        return redirect(url_for("admin.base_datos"))

    registros = info["modelo"].query.all()
    filas = []
    for r in registros:
        filas.append([_valor_columna(r, col) for col in info["columnas"]])

    return render_template(
        "admin/ver_tabla.html",
        etiqueta=info["etiqueta"],
        clave=tabla,
        columnas=info["columnas"],
        filas=filas,
    )


@admin_bp.route("/dashboard")
@login_required
@requiere_rol("Administrador")
def dashboard():
    total_centros = CentroSalud.query.count()
    total_usuarios = Usuario.query.count()
    total_distritos = Distrito.query.count()
    total_comentarios = Comentario.query.count()

    # Centros por distrito
    centros_por_distrito = (
        db.session.query(Distrito.nombre, func.count(CentroSalud.id))
        .outerjoin(CentroSalud, CentroSalud.distrito_id == Distrito.id)
        .group_by(Distrito.id)
        .all()
    )

    # Centros por tipo
    centros_por_tipo = (
        db.session.query(TipoCentro.nombre, func.count(CentroSalud.id))
        .outerjoin(CentroSalud, CentroSalud.tipo_centro_id == TipoCentro.id)
        .group_by(TipoCentro.id)
        .all()
    )

    # Indice de cobertura aproximado: poblacion del distrito / num centros (evitando division por cero)
    cobertura = []
    for distrito in Distrito.query.all():
        n_centros = CentroSalud.query.filter_by(distrito_id=distrito.id).count()
        indice = round(distrito.poblacion_total / n_centros, 1) if n_centros > 0 else None
        cobertura.append({"distrito": distrito.nombre, "poblacion": distrito.poblacion_total,
                           "centros": n_centros, "indice": indice})

    return render_template(
        "admin/dashboard.html",
        total_centros=total_centros,
        total_usuarios=total_usuarios,
        total_distritos=total_distritos,
        total_comentarios=total_comentarios,
        centros_por_distrito=centros_por_distrito,
        centros_por_tipo=centros_por_tipo,
        cobertura=cobertura,
    )


# Crud de Usuarios 
@admin_bp.route("/usuarios")
@login_required
@requiere_rol("Administrador")
def usuarios():
    lista = Usuario.query.all()
    return render_template("admin/usuarios/usuarios.html", usuarios=lista)


@admin_bp.route("/usuarios/<int:usuario_id>/rol", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def cambiar_rol(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    nuevo_rol_id = request.form.get("rol_id", type=int)
    usuario.rol_id = nuevo_rol_id
    db.session.commit()
    flash(f"Rol de {usuario.nombre} actualizado.", "success")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<int:usuario_id>/toggle", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def toggle_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.activo = not usuario.activo
    db.session.commit()
    flash(f"Usuario {usuario.nombre} {'activado' if usuario.activo else 'desactivado'}.", "info")
    return redirect(url_for("admin.usuarios"))

@admin_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def nuevo_usuario():

    if request.method == "POST":

        usuario = Usuario(
            nombre=request.form.get("nombre"),
            username=request.form.get("username", "").strip().lower(),
            email=request.form.get("email"),
            rol_id=request.form.get("rol_id", type=int),
            distrito_id=request.form.get("distrito_id", type=int) or None,
            activo=True
        )

        usuario.set_password(request.form.get("password"))

        db.session.add(usuario)
        db.session.commit()

        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("admin.usuarios"))

    roles = Rol.query.order_by(Rol.nombre).all()
    distritos = Distrito.query.order_by(Distrito.nombre).all()

    return render_template(
        "admin/usuarios/nuevo_usuario.html",
        roles=roles,
        distritos=distritos
    )
    
@admin_bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def editar_usuario(usuario_id):

    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == "POST":

        usuario.nombre = request.form.get("nombre")
        usuario.username = request.form.get("username")
        usuario.email = request.form.get("email")
        usuario.rol_id = request.form.get("rol_id", type=int)
        usuario.distrito_id = request.form.get("distrito_id", type=int) or None

        db.session.commit()

        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("admin.usuarios"))

    roles = Rol.query.order_by(Rol.nombre).all()
    distritos = Distrito.query.order_by(Distrito.nombre).all()

    return render_template(
        "admin/usuarios/editar_usuario.html",
        usuario=usuario,
        roles=roles,
        distritos=distritos
    )

@admin_bp.route("/usuarios/<int:usuario_id>/eliminar", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def eliminar_usuario(usuario_id):

    usuario = Usuario.query.get_or_404(usuario_id)

    db.session.delete(usuario)
    db.session.commit()

    flash("Usuario eliminado correctamente.", "info")
    return redirect(url_for("admin.usuarios"))


# CRUD de Distritos 
@admin_bp.route("/distritos", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def distritos():
    if request.method == "POST":
        d = Distrito(
            nombre=request.form.get("nombre"),
            poblacion_total=request.form.get("poblacion_total", type=int) or 0,
            superficie_km2=request.form.get("superficie_km2", type=float) or 0,
        )
        db.session.add(d)
        db.session.commit()
        flash("Distrito creado.", "success")
        return redirect(url_for("admin.distritos"))

    lista = Distrito.query.order_by(Distrito.nombre).all()
    return render_template("admin/distritos/distritos.html", distritos=lista)


@admin_bp.route("/distritos/<int:distrito_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def editar_distrito(distrito_id):
    d = Distrito.query.get_or_404(distrito_id)

    if request.method == "POST":
        d.nombre = request.form.get("nombre")
        d.poblacion_total = request.form.get("poblacion_total", type=int) or 0
        d.superficie_km2 = request.form.get("superficie_km2", type=float) or 0

        db.session.commit()
        flash("Distrito actualizado.", "success")
        return redirect(url_for("admin.distritos"))

    return render_template("admin/distritos/editar_distrito.html", distrito=d)


@admin_bp.route("/distritos/<int:distrito_id>/eliminar", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def eliminar_distrito(distrito_id):
    d = Distrito.query.get_or_404(distrito_id)
    db.session.delete(d)
    db.session.commit()
    flash("Distrito eliminado.", "info")
    return redirect(url_for("admin.distritos"))



# ---------- CRUD de Especialidades ----------
@admin_bp.route("/especialidades", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def especialidades():
    if request.method == "POST":
        s = Especialidad(nombre=request.form.get("nombre"), descripcion=request.form.get("descripcion"))
        db.session.add(s)
        db.session.commit()
        flash("Especialidad creado.", "success")
        return redirect(url_for("admin.especialidades"))

    lista = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template("admin/especialidades/especialidades.html", especialidades=lista)


@admin_bp.route("/especialidades/<int:especialidad_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador")
def editar_especialidad(especialidad_id):

    s = Especialidad.query.get_or_404(especialidad_id)

    if request.method == "POST":
        s.nombre = request.form.get("nombre")
        s.descripcion = request.form.get("descripcion")

        db.session.commit()
        flash("Especialidad actualizado.", "success")
        return redirect(url_for("admin.especialidades"))

    return render_template("admin/especialidades/editar_especialidad.html", especialidad=s)


@admin_bp.route("/especialidades/<int:especialidad_id>/eliminar", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def eliminar_especialidad(especialidad_id):
    s = Especialidad.query.get_or_404(especialidad_id)
    db.session.delete(s)
    db.session.commit()
    flash("Especialidad eliminado.", "info")
    return redirect(url_for("admin.especialidades"))
