from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.centros import centros_bp
from app.extensions import db
from app.models import CentroSalud, Distrito, TipoCentro, Especialidad, CentroEspecialidad
from app.utils import requiere_rol


@centros_bp.route("/")
@login_required
@requiere_rol("Administrador", "Gestor")
def listar():
    if current_user.tiene_rol("Gestor") and current_user.distrito_id:
        centros = CentroSalud.query.filter_by(distrito_id=current_user.distrito_id).all()
    else:
        centros = CentroSalud.query.all()
    return render_template("centros/listar.html", centros=centros)


@centros_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador", "Gestor")
def nuevo():
    distritos = Distrito.query.order_by(Distrito.nombre).all()
    tipos = TipoCentro.query.order_by(TipoCentro.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()

    if request.method == "POST":
        centro = CentroSalud(
            nombre=request.form.get("nombre"),
            tipo_centro_id=request.form.get("tipo_centro_id", type=int),
            distrito_id=request.form.get("distrito_id", type=int),
            direccion=request.form.get("direccion"),
            latitud=request.form.get("latitud", type=float),
            longitud=request.form.get("longitud", type=float),
            capacidad=request.form.get("capacidad", type=int) or 0,
            horario=request.form.get("horario"),
            telefono=request.form.get("telefono"),
            estado=request.form.get("estado", "Activo"),
        )
        db.session.add(centro)
        db.session.flush()  # para obtener centro.id antes del commit

        especialidades_ids = request.form.getlist("especialidades")
        for sid in especialidades_ids:
            db.session.add(CentroEspecialidad(centro_id=centro.id, especialidad_id=int(sid)))

        db.session.commit()
        flash("Centro de salud creado correctamente.", "success")
        return redirect(url_for("centros.listar"))

    return render_template(
        "centros/formulario.html", centro=None, distritos=distritos, tipos=tipos, especialidades=especialidades
    )


@centros_bp.route("/<int:centro_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol("Administrador", "Gestor")
def editar(centro_id):
    centro = CentroSalud.query.get_or_404(centro_id)
    distritos = Distrito.query.order_by(Distrito.nombre).all()
    tipos = TipoCentro.query.order_by(TipoCentro.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    especialidades_actuales = [cs.especialidad_id for cs in centro.especialidades]

    if request.method == "POST":
        centro.nombre = request.form.get("nombre")
        centro.tipo_centro_id = request.form.get("tipo_centro_id", type=int)
        centro.distrito_id = request.form.get("distrito_id", type=int)
        centro.direccion = request.form.get("direccion")
        centro.latitud = request.form.get("latitud", type=float)
        centro.longitud = request.form.get("longitud", type=float)
        centro.capacidad = request.form.get("capacidad", type=int) or 0
        centro.horario = request.form.get("horario")
        centro.telefono = request.form.get("telefono")
        centro.estado = request.form.get("estado", "Activo")

        CentroEspecialidad.query.filter_by(centro_id=centro.id).delete()
        especialidades_ids = request.form.getlist("especialidades")
        for sid in especialidades_ids:
            db.session.add(CentroEspecialidad(centro_id=centro.id, especialidad_id=int(sid)))

        db.session.commit()
        flash("Centro de salud actualizado.", "success")
        return redirect(url_for("centros.listar"))

    return render_template(
        "centros/formulario.html",
        centro=centro,
        distritos=distritos,
        tipos=tipos,
        especialidades=especialidades,
        especialidades_actuales=especialidades_actuales,
    )


@centros_bp.route("/<int:centro_id>/eliminar", methods=["POST"])
@login_required
@requiere_rol("Administrador")
def eliminar(centro_id):
    centro = CentroSalud.query.get_or_404(centro_id)
    db.session.delete(centro)
    db.session.commit()
    flash("Centro de salud eliminado.", "info")
    return redirect(url_for("centros.listar"))
