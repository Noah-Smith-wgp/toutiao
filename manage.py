from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://toutiao:mysql@122.51.161.120:3306/toutiao'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)

db = SQLAlchemy(app)
manager = Manager(app)
Migrate(app=app, db=db)

manager.add_command('db', MigrateCommand)



@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    manager.run()