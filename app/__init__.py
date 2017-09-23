from flask import Flask
from .main import main
from .models import conn
from flask_cors import *
import flask_login
#from .verify_code import verify_code
lm = flask_login.LoginManager()


from .v1 import v1

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123456'
    app.register_blueprint(main)
    app.register_blueprint(v1.v1,url_prefix='/v1')
    #app.register_blueprint(verify_code.code,url_prefix="/check_code")
    lm.login_view = 'v1.login'
    lm.session_protection = 'basic'
    lm.login_message_category = "info"
    CORS(app)
    lm.init_app(app)
    return app
