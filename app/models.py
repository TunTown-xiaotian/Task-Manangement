from app.db import db

class User(db.Model):
    __tablename__ = "users"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)   # 存哈希
    # 关系属性：一个用户有"很多"任务（不是数据库字段，是 ORM 送的）
    todos    = db.relationship("Todo", backref="owner", lazy="dynamic")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Todo(db.Model):
    __tablename__ = "todos"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    completed  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())