import pymysql
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import config

pymysql.install_as_MySQLdb()

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """
    静态资源配置 添加static_url_path='',否则前端访问static 下的图片出现问题
    参考 https://juejin.im/post/5b4aa6b1e51d45191d79da56
    """
    app = Flask(__name__)

    app.config.from_object(config[config_name]())
    db.init_app(app)
    from .api.blueprint import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .web.blueprint import main as main_blueprint
    app.register_blueprint(main_blueprint)
    CORS(app)

    migrate.init_app(app, db)
    return app
