import redis
from flask import Flask, session
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from settings import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)


# 创建一个redis实例
redis_store = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

Session(app)

CORS(app)

manager = Manager(app)

Migrate(app=app, db=db)

manager.add_command('db', MigrateCommand)


@app.route('/')
def index():

    session['id'] = 'abc'
    return 'index'


if __name__ == '__main__':
    manager.run()
