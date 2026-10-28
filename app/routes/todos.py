from flask import Blueprint, jsonify, request, abort, g
from app.models import Todo
from app.utils.auth import auth_required
from app.db import db

todo_bp = Blueprint("todos", __name__)

todo_bp.before_request(auth_required)

@todo_bp.route("/todos", methods=["GET"])
# @login_required
def list_todos():
    # 1. 取参数并校验（复用第 3 课校验思路）
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    if page < 1 or not 1 <= size <= 100:
        return jsonify({"error": "page/size 参数不合法", "code": 400}), 400

    # 2. 动态拼筛选条件
    q = Todo.query.filter_by(user_id=g.current_user_id)
    completed = request.args.get("completed", type=int)   # 不传 = 不过滤
    if completed in (0, 1):
        q = q.filter_by(completed=bool(completed))

    # 3. 排序白名单：字段名绝不直接吃用户输入
    SORTABLE = {"created_at": Todo.created_at, "id": Todo.id}
    sort_key = request.args.get("sort", "created_at")
    column = SORTABLE.get(sort_key, Todo.created_at)
    q = q.order_by(column.desc() if request.args.get("order") == "desc" else column.asc())

    # 4. 分页并返回标准结构
    pagination = q.paginate(page=page, per_page=size, error_out=False)
    return jsonify({
        "items": [{"id": t.id, "title": t.title, "completed": t.completed}
                 for t in pagination.items],
        "total": pagination.total,
        "page": page,
        "pages": pagination.pages
    })

@todo_bp.route("/todos", methods=["POST"])
def create():
    data = request.json or {}
    from app.models import Todo
    todo = Todo(title=data["title"], user_id=g.current_user_id)
    try:
        db.session.add(todo)
        db.session.commit()   # 提交后 todo.id 自动回填
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"id": todo.id, "message": "创建成功"}), 201

@todo_bp.route("/todos/<int:todo_id>", methods=["PUT"])
# @login_required
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=g.current_user_id).first()
    if not todo:
        return jsonify({"error": "任务不存在或无权限", "code": 403}), 403
    data = request.json or {}
    if "title" in data:
        todo.title = data["title"]        # 改属性 = 改数据
    if "completed" in data:
        todo.completed = bool(data["completed"])
    db.session.commit()
    return jsonify({"message": "更新成功"})

@todo_bp.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = Todo.query.filter_by(id=id).first()    # Flask-SQLAlchemy 3.x
    if todo is None:
        return jsonify({"error": "todo not found"}), 404
    try:
        db.session.delete(todo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return jsonify({"message": "任务已删除", "id": id}), 200

@todo_bp.route("/todos/<int:id>")
def complete_todo(todo_id):
    # sql = "SELECT * FROM todos WHERE id = %s and user_id = %s"
    msg = Todo.query.filter_by(id=todo_id,user_id=g.current_user_id)
    return jsonify(msg)

