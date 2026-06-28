from flask import render_template, jsonify, request, redirect, url_for, flash
from flask_login import current_user, login_required

from app.blueprints.main import main_bp
from app.extensions import db
from app.models import CentroSalud, Distrito, TipoCentro, Comentario


@main_bp.route("/")
def index():
    distritos = Distrito.query.order_by(Distrito.nombre).all()
    tipos = TipoCentro.query.order_by(TipoCentro.nombre).all()
    return render_template("main/index.html", distritos=distritos, tipos=tipos)


@main_bp.route("/api/centros")
def api_centros():
    """Devuelve los centros en JSON para alimentar el mapa Leaflet."""
    distrito_id = request.args.get("distrito_id", type=int)
    tipo_id = request.args.get("tipo_id", type=int)

    query = CentroSalud.query.filter_by(estado="Activo")
    if distrito_id:
        query = query.filter_by(distrito_id=distrito_id)
    if tipo_id:
        query = query.filter_by(tipo_centro_id=tipo_id)

    centros = query.all()
    data = []
    for c in centros:
        data.append({
            "id": c.id,
            "nombre": c.nombre,
            "direccion": c.direccion,
            "latitud": c.latitud,
            "longitud": c.longitud,
            "tipo": c.tipo_centro.nombre,
            "distrito": c.distrito.nombre,
            "horario": c.horario,
            "telefono": c.telefono,
            "especialidades": [cs.especialidad.nombre for cs in c.especialidades],
        })
    return jsonify(data)


@main_bp.route("/centro/<int:centro_id>", methods=["GET", "POST"])
def detalle_centro(centro_id):
    centro = CentroSalud.query.get_or_404(centro_id)

    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para comentar.", "warning")
            return redirect(url_for("auth.login"))

        calificacion = request.form.get("calificacion", type=int)
        texto = request.form.get("comentario", "").strip()
        nuevo = Comentario(
            usuario_id=current_user.id,
            centro_id=centro.id,
            calificacion=calificacion,
            comentario=texto,
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Comentario enviado, ¡gracias!", "success")
        return redirect(url_for("main.detalle_centro", centro_id=centro.id))

    return render_template("main/detalle_centro.html", centro=centro)
