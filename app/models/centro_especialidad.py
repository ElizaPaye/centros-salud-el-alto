from app.extensions import db

class CentroEspecialidad(db.Model):
    __tablename__ = "centro_especialidad"

    id = db.Column(db.Integer, primary_key=True)
    centro_id = db.Column(db.Integer, db.ForeignKey("centros_salud.id"), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey("especialidades.id"), nullable=False)

    centro = db.relationship("CentroSalud", back_populates="especialidades")
    especialidad = db.relationship("Especialidad", back_populates="centros")

    __table_args__ = (db.UniqueConstraint("centro_id", "especialidad_id", name="uq_centro_especialidad"),)
