from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from settings import Config


def generate_token(user_id):

    s = Serializer(secret_key=Config.SECRET_KEY, expires_in=Config.JWT_EXPIRES_IN)

    token = s.dumps({'user_id': user_id})

    return token.decode()


def check_user_token(token):

    s = Serializer(secret_key=Config.SECRET_KEY, expires_in=Config.JWT_EXPIRES_IN)

    try:
        data = s.loads(token)
    except BadData:
        return None

    return data.get('user_id')
