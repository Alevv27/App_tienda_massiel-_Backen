from flask import Blueprint, jsonify
from models import Usuario, Perfil

user_bp = Blueprint("user", __name__, url_prefix="/api")


def usuario_payload(u: Usuario):
    return {
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "perfil": u.perfil.codigo,
        "empresaId": u.empresa_id
    }


@user_bp.get("/usuarios/<int:usuario_id>")
def get_usuario(usuario_id: int):
    u = Usuario.query.get(usuario_id)
    if not u:
        return jsonify({"ok": False, "error": "No existe"}), 404
    return jsonify({"ok": True, "usuario": usuario_payload(u)})


@user_bp.get("/perfiles")
def get_perfiles():
    perfiles = Perfil.query.all()
    data = [{
        "id": p.id,
        "codigo": p.codigo,
        "administracion": bool(p.administracion),
        "gestion": bool(p.gestion),
        "firmar": bool(p.firmar)
    } for p in perfiles]
    return jsonify({"ok": True, "perfiles": data})
