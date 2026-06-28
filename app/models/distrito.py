from app.extensions import db


class Distrito(db.Model):
    __tablename__ = "distritos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    poblacion_total = db.Column(db.Integer, default=0)
    superficie_km2 = db.Column(db.Float, default=0)

    centros = db.relationship("CentroSalud", back_populates="distrito")
    coberturas = db.relationship("CoberturaSanitaria", back_populates="distrito")
    usuarios = db.relationship("Usuario", back_populates="distrito")

    def __repr__(self):
        return f"<Distrito {self.nombre}>"
