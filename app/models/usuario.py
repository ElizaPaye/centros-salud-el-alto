from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    rol = db.relationship("Rol", back_populates="usuarios")
    distrito = db.relationship("Distrito", back_populates="usuarios")
    comentarios = db.relationship("Comentario", back_populates="usuario")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def tiene_rol(self, *nombres_rol):
        return self.rol.nombre in nombres_rol

    def __repr__(self):
        return f"<Usuario {self.email}>"
