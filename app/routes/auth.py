import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app,abort
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        return {"error": "username 和 password 是必填项"}, 400

    existing = User.query.filter_by(username=username).first()

    if existing is None:
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return {"id": username, "message": "创建成功"}, 201

    abort(409)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = str(data.get("password", ''))

    if not username or not password:
        return jsonify({"error": "缺少用户名或密码", "code": 400}), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password, password):
        return jsonify({"error": "用户名或密码错误", "code": 401}), 401

    token = jwt.encode(
        {"user_id": str(user.id),
         "exp": datetime.now(timezone.utc) + timedelta(hours=2)},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return jsonify({"token": token, "expires_in": 7200})

@auth_bp.route("/users/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = User.query.filter_by(id=id).first()    # Flask-SQLAlchemy 3.x
    if todo is None:
        return jsonify({"error": "todo not found"}), 404
    try:
        db.session.delete(todo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"message": "用户已删除", "id": id}), 200
