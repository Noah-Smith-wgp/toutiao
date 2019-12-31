import redis


class Config(object):
    DEBUG = True

    # 定义MySQL配置
    SQLALCHEMY_DATABASE_URI = 'mysql://toutiao:mysql@122.51.161.120:3306/toutiao'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 定义Redis配置
    REDIS_HOST = '49.232.164.126'
    REDIS_PORT = 6379

    # flask_session的配置信息
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=10)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
