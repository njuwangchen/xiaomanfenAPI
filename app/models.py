__author__ = 'ClarkWong'

from app import app, db
from itsdangerous import JSONWebSignatureSerializer, BadSignature
from passlib.apps import custom_app_context as pwd_context
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self):
        s = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        s = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_time = db.Column(db.DateTime, nullable=False)
    #order status, 0 for not paid, 1 for paid
    status = db.Column(db.Integer, nullable=False)
    tel = db.Column(db.String(200), nullable=False)
    address_line_1 = db.Column(db.String(200), nullable=False)
    address_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(100), nullable=False)
    orderer_name = db.Column(db.String(100), nullable=False)

    orderer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    orderer = db.relationship('User', backref=db.backref('orders', lazy='dynamic'))

    def __init__(self, order_time, tel, address_line_1, city, state, country, zipcode, orderer_name, orderer_id, address_line_2='', status=0):
        self.order_time = order_time
        self.tel = tel
        self.address_line_1 = address_line_1
        self.city = city
        self.state = state
        self.country = country
        self.zipcode = zipcode
        self.orderer_name = orderer_name
        self.orderer_id = orderer_id
        self.status = status
        self.address_line_2 = address_line_2

