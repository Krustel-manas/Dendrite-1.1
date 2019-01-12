from datetime import datetime
from Dendrite import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    tender_request = db.Column(db.String(60))

    def __repr__(self):
        return f"User('{self.username}', '{self.role}', '{self.image_file}')"

class Contract(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending Acknowledgement')
    contract_file = db.Column(db.String(40))
    contract_date = db.Column(db.String(40))
    contract_address = db.Column(db.String(40))
    username = db.Column(db.String(40))
    role = db.Column(db.String(40))

    def __repr__(self):
        return f"Contract('{self.contract_id}', '{self.status}', '{self.contract_date}', '{self.contract_file}')"