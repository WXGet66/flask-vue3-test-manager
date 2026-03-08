import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
mail = Mail()  # 新增邮件扩展

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 绑定扩展到 app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)  # 初始化邮件扩展

    # 注册蓝图
    from app.api import auth, tasks, tags, export
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
    app.register_blueprint(tags.bp, url_prefix='/api/tags')
    app.register_blueprint(export.bp, url_prefix='/api/export')

    return app