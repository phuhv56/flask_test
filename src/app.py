# src/app.py

from flask import Flask
import os

from .config import app_config
from .models import db, bcrypt

from .routes.auth_router import auth_api as auth_blueprint
from .routes.post_router import post_api as post_blueprint

from .shared.FacebookSocial import facebook_bp
from .shared.GoogleSocial import google_bp


def create_app(env_name):
    """
    Create app
    """

    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])

    app.config['SECRET_KEY'] = 'thisissupposedtobesecret'

    # DATABASE INITITAL
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # initializing bcrypt and db
    bcrypt.init_app(app)
    db.init_app(app)


    app.register_blueprint(facebook_bp, url_prefix="/login")
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(post_blueprint, url_prefix='/post')

    @app.route('/', methods=['GET'])
    def index():
        """
        example endpoint
        """
        return 'Congratulations! Your first endpoint is workin'

    return app
