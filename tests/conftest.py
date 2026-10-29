# tests/conftest.py
import os
import pytest

# 在导入 create_app 之前设置环境变量
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
# 假设你的 config.py 中是通过 os.getenv('DATABASE_URL') 来读取的

from app import create_app
from app.db import db

@pytest.fixture()
def app():
    app = create_app(test_conftest={
        "TESTING":True,
        "DATABASE_URL":"sqlite:///:memory:"
    }) # 此时 create_app 内部读取到的已经是 SQLite 配置

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()      # 清理：测试结束，表销毁

@pytest.fixture()
def client(app):
    return app.test_client()   # 模拟浏览器，不发真网络请求

@pytest.fixture()
def auth_headers(client):
    """注册 + 登录一条龙，返回带 Token 的请求头"""
    client.post("/api/register", json={"username": "tester", "password": "123456"})
    resp = client.post("/api/login", json={"username": "tester", "password": "123456"})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}