import redis
from flask import Flask, request, g
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from project.utils.user import check_user_token, verify_jwt_token
from settings import Config, DevelopmentConfig, ProductionConfig, setup_log


# 记录日志
setup_log(DevelopmentConfig)


def get_app(config=Config):
    app = Flask(__name__)

    app.config.from_object(config)

    # # 加载配置类之后在创建db
    # db = SQLAlchemy(app)

    # 创建一个redis实例
    redis_store = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    app.redis_store = redis_store

    Session(app)

    CORS(app)

    return app


app = get_app(DevelopmentConfig)

# 加载配置类之后在创建db
db = SQLAlchemy(app)


@app.before_request
def before_request():

    g.user_id = None
    # 获取token
    authorization = request.headers.get('Authorization')
    if authorization is not None and authorization.startswith('Bearer'):
        token = authorization[7:]
        # 验证token
        # user_id = check_user_token(token)
        user_id = verify_jwt_token(token)
        g.user_id = user_id


# 注册蓝图
from project.apps.home import home_buleprint
app.register_blueprint(home_buleprint)  # home蓝图
from project.apps.user import user_buleprint
app.register_blueprint(user_buleprint)  # user蓝图
