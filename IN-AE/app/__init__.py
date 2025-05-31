# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # 로그인 매니저 초기화
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.public import public_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)  # 공개 페이지 블루프린트 등록
    
    return app

# 사용자 로더 콜백 정의
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(user_id)