from database import db
from domain import Usuario, Credencial, Perfil, PerfilModulo, Modulo


class AuthService:

    @staticmethod
    def _perfil_payload(perfil: Perfil) -> dict:
        flags = {
            "administracion": bool(perfil.administracion),
            "gestion":        bool(perfil.gestion),
            "firmar":         bool(perfil.firmar),
        }

        q = (
            db.session.query(Modulo.codigo, Modulo.nombre)
            .join(PerfilModulo, PerfilModulo.modulo_id == Modulo.id)
            .filter(PerfilModulo.perfil_id == perfil.id, PerfilModulo.enabled == True)
            .order_by(Modulo.codigo)
        )
        modulos = [{"codigo": c, "nombre": n} for (c, n) in q.all()]

        return {"flags": flags, "modulos": modulos}

    @staticmethod
    def _usuario_payload(u: Usuario) -> dict:
        return {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "perfil": u.perfil.codigo,
            "empresaId": u.empresa_id,
        }

    @staticmethod
    def login(email: str, password: str) -> tuple[dict, int]:
        """Devuelve (payload, status_code)."""

        u = Usuario.query.filter(
            Usuario.email == email,
            Usuario.activo == True
        ).first()

        if not u:
            return {"ok": False, "error": "Usuario no encontrado"}, 404

        cred = Credencial.query.filter_by(usuario_id=u.id, password=password).first()
        if not cred:
            return {"ok": False, "error": "Credenciales inválidas"}, 401

        perfil = Perfil.query.get(u.perfil_id)
        permisos = AuthService._perfil_payload(perfil)

        payload = {
            "ok": True,
            "usuario": AuthService._usuario_payload(u),
            "permisos": permisos["flags"],
            "modulos": permisos["modulos"],
        }
        return payload, 200
