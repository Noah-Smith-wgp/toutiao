import redis
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from settings import Config, DevelopmentConfig, ProductionConfig
from project.apps.home import home_buleprint
from project.apps.user import user_buleprint


def get_app(config=Config):
    app = Flask(__name__)

    app.config.from_object(Config)

    # # 加载配置类之后在创建db
    # db = SQLAlchemy(app)

    # 创建一个redis实例
    redis_store = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    Session(app)

    CORS(app)

    return app


app = get_app(DevelopmentConfig)

# 加载配置类之后在创建db
db = SQLAlchemy(app)


# 注册蓝图
app.register_blueprint(home_buleprint)  # home蓝图
app.register_blueprint(user_buleprint)  # user蓝图
