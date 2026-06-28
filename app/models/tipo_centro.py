from app.extensions import db


class TipoCentro(db.Model):
    __tablename__ = "tipos_centro"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)  # Hospital, Centro de Salud, Posta Sanitaria

    centros = db.relationship("CentroSalud", back_populates="tipo_centro")

    def __repr__(self):
        return f"<TipoCentro {self.nombre}>"
