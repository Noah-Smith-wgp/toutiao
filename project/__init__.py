import redis
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from settings import Config
from project.apps.home import home_buleprint
from project.apps.user import user_buleprint


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

# 创建一个redis实例
redis_store = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

Session(app)

CORS(app)

# 注册蓝图
app.register_blueprint(home_buleprint)  # home蓝图
app.register_blueprint(user_buleprint)  # user蓝图
