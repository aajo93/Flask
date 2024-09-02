from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()
app = Flask(__name__)

def create_app():

    #app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOSTNAME'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
    )

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    app.config['POSTS_PER_PAGE'] = 2

    #login = LoginManager(app)
    login.init_app(app)
    #needs to be name of login function
    login.login_view = 'main.login'
    #connect to db
    db.init_app(app)

    from app.views.main import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    return app