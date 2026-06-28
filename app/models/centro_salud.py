from app.extensions import db


class CentroSalud(db.Model):
    __tablename__ = "centros_salud"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    tipo_centro_id = db.Column(db.Integer, db.ForeignKey("tipos_centro.id"), nullable=False)
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), nullable=False)
    direccion = db.Column(db.String(255))
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    capacidad = db.Column(db.Integer, default=0)
    horario = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    estado = db.Column(db.String(20), default="Activo")  # Activo / Inactivo

    tipo_centro = db.relationship("TipoCentro", back_populates="centros")
    distrito = db.relationship("Distrito", back_populates="centros")
    especialidades = db.relationship("CentroEspecialidad", back_populates="centro", cascade="all, delete-orphan")
    comentarios = db.relationship("Comentario", back_populates="centro", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CentroSalud {self.nombre}>"
