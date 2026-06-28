import click

from app.extensions import db, bcrypt
from app.models import (
    Rol, Distrito, Usuario, TipoCentro, Especialidad, CentroSalud,
    CentroEspecialidad, CoberturaSanitaria,
)

def registrar_comandos(app):

    @app.cli.command("init-db")
    def init_db():

        db.drop_all()
        db.create_all()

        # Roles
        rol_admin = Rol(nombre="Administrador")
        rol_gestor = Rol(nombre="Gestor")
        rol_ciudadano = Rol(nombre="Ciudadano")

        db.session.add_all([rol_admin, rol_gestor, rol_ciudadano])
        db.session.commit()
        
        # Datos para  distritos 
        distritos_data = [
            ("Distrito 1", 87997, 10.1),
            ("Distrito 2", 73939, 12.0),
            ("Distrito 3", 144828, 17.8),
            ("Distrito 4", 107147, 18.5),
            ("Distrito 5", 104226, 15.8),
            ("Distrito 6", 90538, 15.4),
            ("Distrito 7", 44535, 26.3),
            ("Distrito 8", 121843, 40.9),
            ("Distrito 9", 1720, 26.9),
            ("Distrito 10", 78530, 6.0),
            ("Distrito 11", 1081, 9.8),
            ("Distrito 12", 19816, 8.3),
            ("Distrito 13", 2085, 135.4),
            ("Distrito 14", 47912, 6.7),
        ]

        distritos = []

        for nombre, poblacion, superficie in distritos_data:
            d = Distrito(
                nombre=nombre,
                poblacion_total=poblacion,
                superficie_km2=superficie
            )
            db.session.add(d)
            distritos.append(d)

        db.session.commit()
        
        #Datos para especialidades
        especialidades_data = [
            # 🔵 Especialidades básicas (primer nivel)
            ("Medicina General", "Atención médica general y primer contacto."),
            ("Odontología", "Salud bucal, prevención y tratamiento dental."),
            ("Pediatría", "Atención médica de niños y adolescentes."),
            ("Ginecología y Obstetricia", "Salud reproductiva, control prenatal y partos."),
            ("Enfermería", "Cuidados básicos, control de signos vitales y apoyo médico."),
            ("Nutrición", "Evaluación y orientación alimentaria."),
            ("Psicología", "Salud mental y apoyo emocional."),
            ("Trabajo Social", "Apoyo social y familiar del paciente."),

            # 🟡 Segundo nivel (hospitales medianos)
            ("Cirugía General", "Procedimientos quirúrgicos generales."),
            ("Medicina Interna", "Diagnóstico y tratamiento de enfermedades complejas."),
            ("Anestesiología", "Manejo del dolor y anestesia en cirugías."),
            ("Traumatología", "Lesiones óseas y musculares."),
            ("Oftalmología", "Enfermedades de los ojos."),
            ("Otorrinolaringología", "Oído, nariz y garganta."),
            ("Urología", "Sistema urinario y reproductivo masculino."),
            ("Cardiología", "Enfermedades del corazón."),
            ("Neurología", "Sistema nervioso y cerebro."),
            ("Gastroenterología", "Sistema digestivo."),
            ("Endocrinología", "Hormonas y metabolismo."),
            ("Reumatología", "Enfermedades articulares."),
            ("Nefrología", "Riñones y sistema renal."),
            ("Fisiatría", "Rehabilitación física."),

            # 🔴 Tercer nivel (alta complejidad)
            ("Oncología Clínica", "Diagnóstico y tratamiento del cáncer."),
            ("Ginecología Oncológica", "Cáncer del sistema reproductor femenino."),
            ("Radioterapia", "Tratamiento del cáncer con radiación."),
            ("Medicina Nuclear", "Diagnóstico avanzado con tecnología nuclear."),
            ("Neonatología", "Atención a recién nacidos críticos."),
            ("Cuidados Intensivos", "Atención a pacientes críticos (UCI)."),
        ]
        
        especialidades = []

        for nombre, descripcion in especialidades_data:
            e = Especialidad(
                nombre=nombre,
                descripcion=descripcion
            )
            db.session.add(e)
            especialidades.append(e)

        db.session.commit()


        # Tipos de centro 
        tipos = [
            TipoCentro(nombre="Hospital"),
            TipoCentro(nombre="Centro de Salud"),
            TipoCentro(nombre="Posta Sanitaria"),
        ]

        db.session.add_all(tipos)
        db.session.commit()

        # Usuario admin
        admin = Usuario(
            nombre="Administrador",
            username="admin",
            rol_id=rol_admin.id,
            activo=True
        )
        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        click.echo("Base de datos creada correctamente.")