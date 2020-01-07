from flask import g, jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
import jwt
from datetime import datetime, timedelta

from settings import Config


# 使用itsdangerous
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


# 使用jwt生成token
def generate_jwt_token(user_id):

    token = jwt.encode(payload={'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=2)}, key=Config.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(payload={'user_id': user_id, 'refresh': True, 'exp': datetime.utcnow() + timedelta(days=14)}, key=Config.SECRET_KEY, algorithm='HS256')

    return token.decode(), refresh_token.decode()


# 验证jwt token
def verify_jwt_token(token):

    try:
        payload = jwt.decode(token, key=Config.SECRET_KEY, algorithms=['HS256'])
    except jwt.PyJWTError:
        return False, None
    else:
        return True, payload


# 登录验证装饰器
def loginrequired(func):
    def wrapper(*args, **kwargs):
        if g.user_id:
            return func(*args, **kwargs)
        else:
            # return {'msg': '请登录'}
            return {'message': 'User must be authorized.'}, 401
    return wrapper
