from domain import Usuario, Perfil


class UserService:

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
    def get_usuario(usuario_id: int) -> tuple[dict, int]:
        u = Usuario.query.get(usuario_id)
        if not u:
            return {"ok": False, "error": "No existe"}, 404

        return {"ok": True, "usuario": UserService._usuario_payload(u)}, 200

    @staticmethod
    def get_perfiles() -> dict:
        perfiles = Perfil.query.all()
        data = [{
            "id": p.id,
            "codigo": p.codigo,
            "administracion": bool(p.administracion),
            "gestion": bool(p.gestion),
            "firmar": bool(p.firmar),
        } for p in perfiles]

        return {"ok": True, "perfiles": data}
