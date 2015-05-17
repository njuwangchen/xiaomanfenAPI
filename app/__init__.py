__author__ = 'ClarkWong'
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from flask.ext.restful import Api
from flask.ext.session import Session

app = Flask(__name__)
app.config.from_object('config')

app.secret_key = 'A0Zr89j/4yX R~XHH!jmN]LWX/,?RT'

db = SQLAlchemy(app)
cor = CORS(app, allow_headers='*', supports_credentials=True)
api = Api(app)
Session(app)

from app import models
from app import user_views, order_views, captcha_views
