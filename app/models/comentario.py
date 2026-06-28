from datetime import datetime
from app.extensions import db


class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    centro_id = db.Column(db.Integer, db.ForeignKey("centros_salud.id"), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)  # 1 a 5
    comentario = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="comentarios")
    centro = db.relationship("CentroSalud", back_populates="comentarios")
