from flask import Flask
from flask_jwt_extended import JWTManager
from sqlalchemy import text

from app.config import BaseConfig
from app.config import register_logger
# 导入定义的蓝图
from app.controllers import user_controller
from app.controllers import exchange_controller

# 导入定义的数据库句柄
from app.models import db
from app.models import User
import app.utils as utils
from app.exchange import seed_exchange_data

def create_app(config_name='BaseConfig'):
    app = Flask(__name__)

    # 根据传入的配置名称加载配置
    if config_name == 'testing':
        from app.config.base_config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config.base_config import BaseConfig
        app.config.from_object(BaseConfig)

    print(f"Loaded configuration: {config_name}")
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    # 将db与flask应用程序关联
    db.init_app(app)

    # 数据库预热与本地仿真数据初始化
    with app.app_context():
        db.session.execute(text('SELECT 1'))
        db.create_all()
        _seed_default_user()
        seed_exchange_data()
        db.session.close()

    # 配置jwt
    jwt = JWTManager(app)

    # 注册Blueprint，并分别指定前缀
    # NOTE 接口定义规范：同属于一个功能模块的接口应当有相似的前缀，以便于管理和维护
    app.register_blueprint(user_controller, url_prefix='/user')
    app.register_blueprint(exchange_controller, url_prefix='/exchange')

    # 配置日志
    app = register_logger(app)


    return app


def _seed_default_user():
    if User.query.filter_by(username='admin').first() is not None:
        return
    user = User(
        username='admin',
        password=utils.encrypt('123456'),
        nickname='AMM Trader',
        email='trader@example.com',
        phone='16666666666',
    )
    db.session.add(user)
    db.session.commit()
