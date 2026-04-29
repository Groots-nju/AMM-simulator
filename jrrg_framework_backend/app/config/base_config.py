import os
from dotenv import load_dotenv

# # 加载env
# load_dotenv('app.env')

# 获取项目根目录路径————————————————————————————————————————————————————————————————————————————
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# 拼接出 app.env 的绝对路径
env_path = os.path.join(BASE_DIR, 'app.env')

# 加载 app.env 文件
load_dotenv(env_path)
# ——————————————————————————————————————————————————————————————————————————————————————————

class BaseConfig:
    # 服务配置
    DEBUG = os.getenv('DEBUG') == 'True'
    TESTING = os.getenv('TESTING') == 'True'

    # 数据库相关配置，NOTE 由于使用Flask-SQLAlchemy，所以下面两个配置名称不能自定义
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or f"sqlite:///{os.path.join(BASE_DIR, 'exchange_simulator.db')}" # 配置url
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 关闭追踪
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,  # 连接池大小
        'max_overflow': 10,  # 最大溢出连接数
        'pool_pre_ping': True,  # 检查连接是否有效
        'pool_recycle': 3600  # 连接回收时间（秒）
    }

    # jwt
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'local_exchange_simulator_secret'
    JWT_TOKEN_LOCATION = ['headers']


class TestingConfig(BaseConfig):
    # 启用测试模式
    TESTING = True
    DEBUG = True

    # 使用内存数据库，避免污染实际数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # 测试用 JWT 密钥
    JWT_SECRET_KEY = 'test_secret_key'
    JWT_TOKEN_LOCATION = ['headers']  # 默认从请求头中获取 Token
