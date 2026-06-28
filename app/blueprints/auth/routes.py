from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models import Usuario, Rol


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password) and usuario.activo:
            login_user(usuario)
            flash(f"Bienvenido, {usuario.nombre}", "success")
            siguiente = request.args.get("next")
            return redirect(siguiente or url_for("main.index"))
        else:
            flash("Credenciales incorrectas o usuario inactivo.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    rol_ciudadano = Rol.query.filter_by(nombre="Ciudadano").first()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if Usuario.query.filter_by(username=username).first():
            flash("Ese nombre de usuario ya está en uso.", "warning")
            return redirect(url_for("auth.registro"))

        nuevo = Usuario(nombre=nombre, username=username, rol_id=rol_ciudadano.id)
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()
        flash("Cuenta creada. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/registro.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.index"))
