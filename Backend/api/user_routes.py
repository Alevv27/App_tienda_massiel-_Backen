from flask import Blueprint, jsonify, request
from services.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/api")

# ---------- USUARIOS ----------

@user_bp.get("/usuarios/<int:usuario_id>")
def get_usuario(usuario_id: int):
    payload, status = UserService.get_usuario(usuario_id)
    return jsonify(payload), status


@user_bp.get("/usuarios")
def list_usuarios():
    payload, status = UserService.list_usuarios()
    return jsonify(payload), status


@user_bp.post("/usuarios")
def create_usuario():
    body = request.get_json(silent=True) or {}
    payload, status = UserService.create_usuario(body)
    return jsonify(payload), status


@user_bp.patch("/usuarios/<int:usuario_id>")
def update_usuario(usuario_id: int):
    body = request.get_json(silent=True) or {}
    payload, status = UserService.update_usuario(usuario_id, body)
    return jsonify(payload), status


@user_bp.delete("/usuarios/<int:usuario_id>")
def delete_usuario(usuario_id: int):
    payload, status = UserService.delete_usuario(usuario_id)
    return jsonify(payload), status


# ---------- PERFILES ----------

@user_bp.get("/perfiles")
def get_perfiles():
    payload, status = UserService.get_perfiles()
    return jsonify(payload), status


@user_bp.post("/perfiles")
def create_perfil():
    body = request.get_json(silent=True) or {}
    payload, status = UserService.create_perfil(body)
    return jsonify(payload), status


@user_bp.patch("/perfiles/<int:perfil_id>")
def update_perfil(perfil_id: int):
    body = request.get_json(silent=True) or {}
    payload, status = UserService.update_perfil(perfil_id, body)
    return jsonify(payload), status


@user_bp.delete("/perfiles/<int:perfil_id>")
def delete_perfil(perfil_id: int):
    payload, status = UserService.delete_perfil(perfil_id)
    return jsonify(payload), status


# ---------- EMPRESAS ----------

@user_bp.get("/empresas")
def get_empresas():
    payload, status = UserService.get_empresas()
    return jsonify(payload), status
