import logging

from flask import Blueprint, current_app
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re

from app.models import db, User
import app.utils as utils

# flask提供Blueprint用于将一个项目按照功能模块拆分，这样一来路由就不需要全部写在app.py中了
# NOTE 项目开发规范：妥善将项目功能进行拆分，便于分工，常用的做法是根据功能对象，例如所有与user相关的接口都放在user_controller.py文件中
# 如下则是创建了一个名为user_controller的蓝图（固定写法），并返回一个名为user_controller的蓝图对象（将来在app.py中使用它）
user_controller = Blueprint('user_controller', __name__)


# 统一为每个请求打印日志，通过“蓝图.before_request”和“蓝图.after_request”
@user_controller.before_request
def log_request_info():
    current_app.logger.info(f"收到请求: {request.method} {request.url}")
@user_controller.after_request
def log_response_info(response):
    current_app.logger.info(f"响应状态码: {response.status_code}")
    return response

# 下面开始是user_controller蓝图下的所有装饰器与配套函数 ——————————————————————————————————————————————————————————

# 使用蓝图之后，定义路由的方式稍微有些变化（仅在于从app变成了对应的Blueprint而已）
# NOTE RESTful风格规范：在定义接口时要根据接口功能选择合适请求方式：GET用于查询、POST用于操作或新增、PUT用于更新、DELETE用于删除等
@user_controller.post('/login')
def user_login():
    """
    处理用户登录
    """
    # 获取用户数据并校验参数
    login_data = request.get_json()
    username, password = login_data['username'], login_data['password']
    if not username or not password:
        return utils.error("参数不合法")

    # 根据username查询出对应记录，由于我们知道username一定是唯一的，所以直接取第一个即可
    db_user = db.session.query(User).filter_by(username=username).first()
    # 验证username是否存在，并且验证传入的密码是否与数据库中的密码“一致”
    if not db_user or not utils.check(password, db_user.password):
        return utils.error(message="用户名或密码不正确", code=401)

    # 到此验证成功
    # 创建jwt，这里需要使用强转（因为identity要求传入的参数必须为str），
    # 额外的信息可以通过additional_claims来获得，切记不要传入password
    token = create_access_token(identity=str(db_user.id), additional_claims={"user_info": {
        "id": db_user.id,
        "username": db_user.username,
        "nickname": db_user.nickname,
        "email": db_user.email,
        "phone": db_user.phone,
    }})
    # 只需要返回code=200即可
    return utils.success(data=token)


@user_controller.post('/logout')
# jwt_required装饰器，添加了该装饰器的controller要求必须携带jwt令牌，
# 并且在controller内部可以通过get_jwt_identity()获取之前存储在其中的用户信息（本例中是id）
@jwt_required()
def user_logout():
    """
    处理用户登出，如果后端实现需要用到Redis，所以这里实际上只返回一个200，具体由前端实现
    """
    # Flask框架提供了current_app变量在其他蓝图中输出日志
    current_app.logger.info("用户id=%s", get_jwt_identity())
    return utils.success()


def validate_register_data(register_data):
    """
    校验注册数据的工具函数
    :param register_data: Dict 前端提交的用户注册的数据
    :return: 数据是否满足校验标准
    """
    # 定义校验邮箱和中国大陆手机号的正则表达式
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    phone_pattern = r'^1[3-9]\d{9}$'
    # 主要是校验各个字段不能为空，并且长度介于1~255之间
    if not "username" in register_data or not "password" in register_data or not "phone" in register_data or not "email" in register_data or not "phone" in register_data:
        return False
    if not register_data["username"] or len(register_data["username"]) > 255 or not register_data["password"] or len(register_data["password"]) > 255 or not register_data["nickname"] or len(register_data["nickname"]) > 255 or not register_data["email"] or re.match(email_pattern, register_data["email"]) is None or not register_data["phone"] or re.match(phone_pattern, register_data["phone"]) is None:
        return False
    return True

@user_controller.post('/register')
def user_register():
    """
    处理用户注册
    """
    # 获取数据
    register_data = request.get_json(force=True)
    # NOTE 更规范的做法是使用类似于marshmallow的参数校验库，但为了方便上手这里采用手动校验
    if not validate_register_data(register_data):
        # 校验失败则返回
        return utils.error("参数不合法")
    user = User(username=register_data['username'], password=register_data['password'], email=register_data['email'], nickname=register_data['nickname'], phone=register_data['phone'])
    # 为password加密
    user.password = utils.encrypt(user.password)
    # 操作数据库
    db.session.add(user)
    db.session.commit() # 别忘了commit
    # 返回操作成功
    return utils.success()

@user_controller.get('/query')# 与前端对齐接口
@jwt_required() # 确保用户已登录
def get_user_info():
    """
    获取当前登录用户的信息
    """
    user_id = get_jwt_identity() # 获取token中的用户ID
    db_user = db.session.query(User).filter_by(id=user_id).first()

    if not db_user:
        return utils.error(message="用户不存在", code=404)

    # 提供给前端的用户信息，不能包含密码！！
    user_data = {
        "id": db_user.id,
        "username": db_user.username,
        "nickname": db_user.nickname,
        "email": db_user.email,
        "phone": db_user.phone
    }

    return utils.success(data=user_data)


# 用不到这个函数，“注销”在前端调用的函数是logout，也就是上面那个函数
# @user_controller.delete('/delete')  # 与前端对齐接口
# @jwt_required()     # 确保用户已登录
# def user_delete():
#     """
#     处理用户注销账户
#     """
#     user_id = get_jwt_identity()
#     db_user = db.session.query(User).filter_by(id=user_id).first()
#
#     if not db_user:
#         return utils.error(message="用户不存在", code=404)
#     # 从数据库中删除该用户的信息
#     db.session.delete(db_user)
#     db.session.commit()
#     return utils.success()


@user_controller.put('/modify')
@jwt_required()
def user_modify():
    """
    用户信息修改接口（PUT请求）
    请求示例：
    {
        "username": "new_name",  // 五选一字段，每次只唯一修改一个字段
    }
    """
    # 获取认证用户
    user_id = get_jwt_identity()
    db_user = db.session.query(User).filter_by(id=user_id).first()
    if not db_user:
        return utils.error("用户不存在", code=404)

    # 参数校验
    modify_data = request.get_json()
    # 允许修改的字段列表
    valid_fields = {'username', 'nickname', 'email', 'phone', 'password'}

    # 验证请求参数：只能包含一个有效字段且值有效
    provided_fields = set(modify_data.keys()) & valid_fields
    if len(provided_fields) != 1:   # 按道理是不会出现这种情况的()
        return utils.error("每次只能修改一个字段", code=400)

    field = provided_fields.pop()  # 确认到底用户要修改哪一个信息
    new_value = modify_data[field].strip() if isinstance(modify_data[field], str) else modify_data[field]

    # 基础校验：非空和长度（密码单独处理）
    if field != 'password' and (not new_value or len(new_value) > 255):
        return utils.error(f"{field} 不能为空 也不能超过255字符", code=400)

    # 处理不同字段
    if field == 'username':
        if User.query.filter(User.username == new_value, User.id != user_id).first():
            return utils.error("用户名已存在", code=409)
        db_user.username = new_value

    elif field == 'email':
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', new_value):
            return utils.error("邮箱格式错误", code=400)
        db_user.email = new_value

    elif field == 'phone':
        if not re.match(r'^1[3-9]\d{9}$', new_value):
            return utils.error("手机号格式错误", code=400)
        db_user.phone = new_value

    elif field == 'password':
        if len(new_value) < 6:
            return utils.error("密码至少需要6位", code=400)
        db_user.password = utils.encrypt(new_value)

    else:  # nickname
        db_user.nickname = new_value

        # 提交修改
    db.session.commit()

    return utils.success("修改成功")

