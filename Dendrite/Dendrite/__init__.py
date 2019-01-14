from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair, CryptoKeypair

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'Dendrite/static/Contracts/'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "loginpage"
login_manager.login_message_category = "info"
BIGCHAIN_IP = 'http://127.0.0.1'
bdb = BigchainDB(f'{BIGCHAIN_IP}:9984/')

from Dendrite import routes