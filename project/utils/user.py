from flask import g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from settings import Config


# 生成token
def generate_token(user_id):

    s = Serializer(secret_key=Config.SECRET_KEY, expires_in=Config.JWT_EXPIRES_IN)

    token = s.dumps({'user_id': user_id})

    return token.decode()


# 验证token
def check_user_token(token):

    s = Serializer(secret_key=Config.SECRET_KEY, expires_in=Config.JWT_EXPIRES_IN)

    try:
        data = s.loads(token)
    except BadData:
        return None

    return data.get('user_id')


# 登录验证装饰器
def loginrequired(func):
    def wrapper(*args, **kwargs):
        if g.user_id:
            return func(*args, **kwargs)
        else:
            return {'msg': '请登录'}
    return wrapper
