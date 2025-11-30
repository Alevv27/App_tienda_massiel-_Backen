from typing import Dict
from database import db
from domain import Usuario, Perfil, Empresa, Credencial, Modulo, PerfilModulo


class UserService:

    # ---------- HELPERS ----------
    @staticmethod
    def _usuario_payload(u: Usuario) -> dict:
        return {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "perfil": u.perfil.codigo if u.perfil else None,
            "empresaId": u.empresa_id,
            "activo": bool(u.activo),
        }

    @staticmethod
    def _perfil_payload(p: Perfil) -> dict:
        return {
            "id": p.id,
            "codigo": p.codigo,
            "administracion": bool(p.administracion),
            "gestion": bool(p.gestion),
            "firmar": bool(p.firmar),
        }

    # ========== USUARIOS ==========

    @staticmethod
    def get_usuario(usuario_id: int) -> tuple[dict, int]:
        u = Usuario.query.get(usuario_id)
        if not u:
            return {"ok": False, "error": "No existe"}, 404
        return {"ok": True, "usuario": UserService._usuario_payload(u)}, 200

    @staticmethod
    def list_usuarios() -> tuple[dict, int]:
        usuarios = Usuario.query.order_by(Usuario.id).all()
        data = [UserService._usuario_payload(u) for u in usuarios]
        return {"ok": True, "usuarios": data}, 200

    @staticmethod
    def create_usuario(body: Dict) -> tuple[dict, int]:
        nombre = (body.get("nombre") or "").strip()
        email = (body.get("email") or "").strip().lower()
        password = (body.get("password") or "")
        perfil_id = body.get("perfil_id")
        empresa_id = body.get("empresa_id")

        if not all([nombre, email, password, perfil_id, empresa_id]):
            return {"ok": False, "error": "Faltan campos obligatorios"}, 400

        if Usuario.query.filter_by(email=email).first():
            return {"ok": False, "error": "El email ya está registrado"}, 409

        if not Perfil.query.get(perfil_id):
            return {"ok": False, "error": "Perfil no existe"}, 400

        if not Empresa.query.get(empresa_id):
            return {"ok": False, "error": "Empresa no existe"}, 400

        u = Usuario(
            nombre=nombre,
            email=email,
            perfil_id=perfil_id,
            empresa_id=empresa_id,
            activo=True,
        )
        db.session.add(u)
        db.session.flush()  # necesitamos u.id

        cred = Credencial(usuario_id=u.id, password=password)
        db.session.add(cred)

        db.session.commit()

        return {"ok": True, "usuario": UserService._usuario_payload(u)}, 201

    @staticmethod
    def update_usuario(usuario_id: int, body: Dict) -> tuple[dict, int]:
        u = Usuario.query.get(usuario_id)
        if not u:
            return {"ok": False, "error": "No existe"}, 404

        nombre = body.get("nombre")
        email = body.get("email")
        perfil_id = body.get("perfil_id")
        empresa_id = body.get("empresa_id")
        activo = body.get("activo")

        if nombre is not None:
            u.nombre = nombre.strip()
        if email is not None:
            email = email.strip().lower()
            if Usuario.query.filter(Usuario.id != u.id, Usuario.email == email).first():
                return {"ok": False, "error": "El email ya está en uso"}, 409
            u.email = email
        if perfil_id is not None:
            if not Perfil.query.get(perfil_id):
                return {"ok": False, "error": "Perfil no existe"}, 400
            u.perfil_id = perfil_id
        if empresa_id is not None:
            if not Empresa.query.get(empresa_id):
                return {"ok": False, "error": "Empresa no existe"}, 400
            u.empresa_id = empresa_id
        if activo is not None:
            u.activo = bool(activo)

        db.session.commit()
        return {"ok": True, "usuario": UserService._usuario_payload(u)}, 200

    @staticmethod
    def delete_usuario(usuario_id: int) -> tuple[dict, int]:
        u = Usuario.query.get(usuario_id)
        if not u:
            return {"ok": False, "error": "No existe"}, 404

        Credencial.query.filter_by(usuario_id=usuario_id).delete()
        db.session.delete(u)
        db.session.commit()
        return {"ok": True}, 200

    # ========== PERFILES ==========

    @staticmethod
    def get_perfiles() -> tuple[dict, int]:
        perfiles = Perfil.query.order_by(Perfil.codigo).all()
        data = [UserService._perfil_payload(p) for p in perfiles]
        return {"ok": True, "perfiles": data}, 200

    @staticmethod
    def create_perfil(body: Dict) -> tuple[dict, int]:
        codigo = (body.get("codigo") or "").strip().upper()
        if not codigo:
            return {"ok": False, "error": "codigo es obligatorio"}, 400

        if Perfil.query.filter_by(codigo=codigo).first():
            return {"ok": False, "error": "El código de perfil ya existe"}, 409

        administracion = bool(body.get("administracion", False))
        gestion = bool(body.get("gestion", False))
        firmar = bool(body.get("firmar", False))

        perfil = Perfil(
            codigo=codigo,
            administracion=administracion,
            gestion=gestion,
            firmar=firmar,
        )
        db.session.add(perfil)
        db.session.flush()

        # PerfilModulo según flags
        modulos = Modulo.query.all()
        for m in modulos:
            enabled = False
            if m.codigo == "ADMINISTRACION":
                enabled = administracion
            elif m.codigo == "GESTION":
                enabled = gestion
            elif m.codigo == "FIRMAR":
                enabled = firmar

            pm = PerfilModulo(
                perfil_id=perfil.id,
                modulo_id=m.id,
                enabled=enabled,
            )
            db.session.add(pm)

        db.session.commit()
        return {"ok": True, "perfil": UserService._perfil_payload(perfil)}, 201

    @staticmethod
    def update_perfil(perfil_id: int, body: Dict) -> tuple[dict, int]:
        perfil = Perfil.query.get(perfil_id)
        if not perfil:
            return {"ok": False, "error": "Perfil no existe"}, 404

        codigo = body.get("codigo")
        if codigo is not None:
            codigo = codigo.strip().upper()
            if Perfil.query.filter(Perfil.id != perfil.id, Perfil.codigo == codigo).first():
                return {"ok": False, "error": "El código de perfil ya existe"}, 409
            perfil.codigo = codigo

        if "administracion" in body:
            perfil.administracion = bool(body["administracion"])
        if "gestion" in body:
            perfil.gestion = bool(body["gestion"])
        if "firmar" in body:
            perfil.firmar = bool(body["firmar"])

        db.session.commit()
        return {"ok": True, "perfil": UserService._perfil_payload(perfil)}, 200

    @staticmethod
    def delete_perfil(perfil_id: int) -> tuple[dict, int]:
        perfil = Perfil.query.get(perfil_id)
        if not perfil:
            return {"ok": False, "error": "Perfil no existe"}, 404

        if Usuario.query.filter_by(perfil_id=perfil_id).first():
            return {"ok": False, "error": "Hay usuarios asociados a este perfil"}, 400

        PerfilModulo.query.filter_by(perfil_id=perfil_id).delete()
        db.session.delete(perfil)
        db.session.commit()
        return {"ok": True}, 200

    # ========== EMPRESAS ==========

    @staticmethod
    def get_empresas() -> tuple[dict, int]:
        empresas = Empresa.query.order_by(Empresa.nombre).all()
        data = [{"id": e.id, "nombre": e.nombre} for e in empresas]
        return {"ok": True, "empresas": data}, 200
