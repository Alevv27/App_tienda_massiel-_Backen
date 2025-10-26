from database import db

# ----- Empresa -----
class Empresa(db.Model):
    __tablename__ = "Empresa"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)


# ----- Perfil -----
class Perfil(db.Model):
    __tablename__ = "Perfil"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # ADMIN|GESTOR|FIRMANTE
    administracion = db.Column(db.Boolean, nullable=False, default=False)
    gestion        = db.Column(db.Boolean, nullable=False, default=False)
    firmar         = db.Column(db.Boolean, nullable=False, default=False)

    modulos = db.relationship("PerfilModulo", back_populates="perfil")


# ----- Usuario -----
class Usuario(db.Model):
    __tablename__ = "Usuario"
    __table_args__ = {"schema": "dbo"}
    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    perfil_id  = db.Column(db.Integer, db.ForeignKey("dbo.Perfil.id"), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey("dbo.Empresa.id"), nullable=False)
    activo     = db.Column(db.Boolean, nullable=False, default=True)

    perfil     = db.relationship("Perfil")
    empresa    = db.relationship("Empresa")
    credencial = db.relationship("Credencial", uselist=False, back_populates="usuario")


# ----- Credencial -----
class Credencial(db.Model):
    __tablename__ = "Credencial"
    __table_args__ = {"schema": "dbo"}
    usuario_id = db.Column(db.Integer, db.ForeignKey("dbo.Usuario.id"), primary_key=True)
    password   = db.Column(db.String(120), nullable=False)  # ⚠️ usar hash en producción

    usuario = db.relationship("Usuario", back_populates="credencial")


# ----- Modulo -----
class Modulo(db.Model):
    __tablename__ = "Modulo"
    __table_args__ = {"schema": "dbo"}
    id     = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)


# ----- PerfilModulo (puente) -----
class PerfilModulo(db.Model):
    __tablename__ = "PerfilModulo"
    __table_args__ = {"schema": "dbo"}
    perfil_id = db.Column(db.Integer, db.ForeignKey("dbo.Perfil.id"), primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey("dbo.Modulo.id"), primary_key=True)
    enabled   = db.Column(db.Boolean, nullable=False, default=True)

    perfil = db.relationship("Perfil", back_populates="modulos")
    modulo = db.relationship("Modulo")
