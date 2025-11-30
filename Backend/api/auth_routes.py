from flask import Blueprint, request, jsonify
from domain.models import Usuario, Credencial, Perfil, PerfilModulo, Modulo
from database import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def perfil_payload(perfil: Perfil):
    flags = {
        "administracion": bool(perfil.administracion),
        "gestion":        bool(perfil.gestion),
        "firmar":         bool(perfil.firmar)
    }
    q = (
        db.session.query(Modulo.codigo, Modulo.nombre)
        .join(PerfilModulo, PerfilModulo.modulo_id == Modulo.id)
        .filter(PerfilModulo.perfil_id == perfil.id, PerfilModulo.enabled == True)
        .order_by(Modulo.codigo)
    )
    modulos = [{"codigo": c, "nombre": n} for (c, n) in q.all()]
    return {"flags": flags, "modulos": modulos}


def usuario_payload(u: Usuario):
    return {
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "perfil": u.perfil.codigo,
        "empresaId": u.empresa_id
    }


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = (body.get("password") or "")

    u = Usuario.query.filter(
        Usuario.email == email,
        Usuario.activo == True
    ).first()

    if not u:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404

    cred = Credencial.query.filter_by(usuario_id=u.id, password=password).first()
    if not cred:
        return jsonify({"ok": False, "error": "Credenciales inválidas"}), 401

    perfil = Perfil.query.get(u.perfil_id)
    permisos = perfil_payload(perfil)

    return jsonify({
        "ok": True,
        "usuario": usuario_payload(u),
        "permisos": permisos["flags"],
        "modulos": permisos["modulos"]
    }), 200
