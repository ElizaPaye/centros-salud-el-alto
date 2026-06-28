from app.extensions import db


class CoberturaSanitaria(db.Model):
    __tablename__ = "cobertura_sanitaria"

    id = db.Column(db.Integer, primary_key=True)
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    poblacion = db.Column(db.Integer, default=0)
    num_centros = db.Column(db.Integer, default=0)
    indice_cobertura = db.Column(db.Float, default=0)  # ej: habitantes por centro de salud

    distrito = db.relationship("Distrito", back_populates="coberturas")

    def __repr__(self):
        return f"<Cobertura {self.distrito_id}-{self.anio}>"
