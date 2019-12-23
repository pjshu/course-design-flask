import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import config

pymysql.install_as_MySQLdb()

db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name]())
    db.init_app(app)
    from .api.blueprint import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .web.blueprint import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
