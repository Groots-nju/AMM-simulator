from app.models import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    nickname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(11))

    # ✅ 新增字段
    risk_level = db.Column(db.String(20))  # 对应数据库里的 VARCHAR(20)
    preferred_horizen = db.Column(db.String(20))  # 对应数据库里的 VARCHAR(20)
    preferred_investment = db.Column(db.JSON)  # 对应数据库里的 JSON 类型

    # 用于debug
    def __repr__(self):
        return '<User %r>' % self.username
