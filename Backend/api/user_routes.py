from flask import Blueprint, jsonify
from services.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/api")


@user_bp.get("/usuarios/<int:usuario_id>")
def get_usuario(usuario_id: int):
    payload, status = UserService.get_usuario(usuario_id)
    return jsonify(payload), status


@user_bp.get("/perfiles")
def get_perfiles():
    payload = UserService.get_perfiles()
    return jsonify(payload), 200
