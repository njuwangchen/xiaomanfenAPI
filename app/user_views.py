__author__ = 'ClarkWong'

from app import db, api, app
from models import User
from flask.ext.restful import reqparse, abort, Resource, fields, marshal_with
from flask import request
import requests
import json

login_fields = {
    "isSucceed": fields.Boolean,
    "emailNotExist": fields.Boolean,
    "passwdNotRight": fields.Boolean,
    "loginEmail": fields.String,
    "token": fields.String
}

register_fields = {
    "isSucceed": fields.Boolean,
    "emailExist": fields.Boolean,
    "loginEmail": fields.String,
    "token": fields.String
}

class LoginApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=unicode, required=True, location='json')
        self.parser.add_argument('password', type=unicode, required=True, location='json')
        self.parser.add_argument('captcha', type=dict, required=True, location='json')
        super(LoginApi, self).__init__()

    @marshal_with(login_fields)
    def post(self):
        result = dict()
        args = self.parser.parse_args()

        captcha_payload = dict()
        captcha_payload['response'] = args['captcha']['response']
        captcha_payload['secret'] = app.config['RECAPTCHA_KEY']
        captcha_payload['remoteip'] = request.remote_addr

        payload = {'secret': app.config['RECAPTCHA_KEY'], 'response': args['captcha']['response'], 'remoteip': request.remote_addr}
        print(payload)
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', params=payload)
        r = r.json()
        print(r)
        user = User.query.filter_by(email=args['email']).first()
        if not user:
            result['isSucceed'] = False
            result['emailNotExist'] = True
        elif not user.verify_password(args['password']):
            result['isSucceed'] = False
            result['passwdNotRight'] = True
        else:
            result['isSucceed'] = True
            result['loginEmail'] = user.email
            result['token'] = user.generate_auth_token()

        return result, 201

class RegisterApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=unicode, required=True, location='json')
        self.parser.add_argument('password', type=unicode, required=True, location='json')
        super(RegisterApi, self).__init__()

    @marshal_with(register_fields)
    def post(self):
        result = dict()
        args = self.parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if user:
            result['isSucceed'] = False
            result['emailExist'] = True
        else:
            user = User(args['email'], args['password'])
            db.session.add(user)
            db.session.commit()
            result['isSucceed'] = True
            result['loginEmail'] = user.email
            result['token'] = user.generate_auth_token()

        return result, 201

# class RegisterApi(Resource):
#     def __init__(self):
#         self.parser = reqparse.RequestParser()
#         self.parser.add_argument('email', type=unicode, required=True, location='json')
#         self.parser.add_argument('password', type=unicode, reqparse=True, location='json')
#         super(RegisterApi, self).__init__()
#
#     @marshal_with(register_fields)
#     def post(self):
#         result = dict()
#         args = self.parser.parse_args()
#         user = User.query.filter_by(email=args['email']).first()
#         if user:
#             result['isSucceed'] = False
#             result['emailExist'] = True
#         else:
#             user = User(args['email'], args['password'])
#             db.session.add(user)
#             db.session.commit()
#             result['isSucceed'] = True
#             result['loginEmail'] = user.email
#             result['token'] = user.generate_auth_token()
#
#         return result, 201
#

api.add_resource(LoginApi, '/api/v1/login', endpoint='login')
api.add_resource(RegisterApi, '/api/v1/register', endpoint='register')
# api.add_resource(RegisterApi, '/api/v1/register', endpoint='register')