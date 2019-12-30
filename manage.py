import redis
from flask import Flask, session
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)


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
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


app.config.from_object(Config)

db = SQLAlchemy(app)
manager = Manager(app)

# 创建一个redis实例
redis_store = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

Session(app)

CORS(app)

Migrate(app=app, db=db)

manager.add_command('db', MigrateCommand)


@app.route('/')
def index():

    session['id'] = 'abc'
    return 'index'


if __name__ == '__main__':
    manager.run()
