# -*- coding: utf-8 -*-

from app import db, api, app
from models import Order, User
from flask.ext.restful import reqparse, abort, Resource, fields, marshal_with
from datetime import datetime
from flask import request
import requests
from werkzeug.datastructures import ImmutableOrderedMultiDict

order_operation_result_fields = {
    "isSucceed": fields.Boolean,
    "order_id": fields.Integer
}

order_fields = {
    "id": fields.Integer,
    "order_time": fields.String,
    "status": fields.Integer,
    "status_str": fields.String,
    "tel": fields.String,
    "address_line_1": fields.String,
    "address_line_2": fields.String,
    "city": fields.String,
    "state": fields.String,
    "country": fields.String,
    "zipcode": fields.String,
    "orderer_name": fields.String,
    "type": fields.Integer
}

class OrderApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=unicode, required=True, location='headers')
        self.parser.add_argument('tel', type=unicode, required=True, location='json')
        self.parser.add_argument('address_line_1', type=unicode, required=True, location='json')
        self.parser.add_argument('address_line_2', type=unicode, location='json')
        self.parser.add_argument('city', type=unicode, required=True, location='json')
        self.parser.add_argument('state', type=unicode, required=True, location='json')
        self.parser.add_argument('country', type=unicode, required=True, location='json')
        self.parser.add_argument('zipcode', type=unicode, required=True, location='json')
        self.parser.add_argument('orderer_name', type=unicode, required=True, location='json')
        self.parser.add_argument('type', type=unicode, required=True, location='json')
        super(OrderApi, self).__init__()

    @marshal_with(order_operation_result_fields)
    def post(self):
        args = self.parser.parse_args()
        user = User.verify_auth_token(args['token'])
        result = {}
        if user:
            order_time = datetime.now()
            order = Order(order_time, args['tel'], args['address_line_1'], args['city'], args['state'], args['country'], args['zipcode'], args['orderer_name'], user.id, args['address_line_2'], 0)
            db.session.add(order)
            db.session.commit()
            result['isSucceed'] = True
            result['order_id'] = order.id
            return result, 201
        else:
            result['isSucceed'] = False
            return result, 201

class OrderListApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=unicode, required=True, location='headers')
        super(OrderListApi, self).__init__()

    @marshal_with(order_fields)
    def get(self):
        args = self.parser.parse_args()
        user = User.verify_auth_token(args['token'])
        if user:
            orders = user.orders.all()
            for order in orders:
                if order.status == 0:
                    order.status_str = u'未付款'
                elif order.status == 1:
                    order.status_str = u'已付款'
                else:
                    order.status_str = u'未知状态'
            return orders, 201
        else:
            abort(400)

@app.route('/api/v1/ipn',methods=['POST'])
def ipn():
    arg = ''
    #: We use an ImmutableOrderedMultiDict item because it retains the order.
    request.parameter_storage_class = ImmutableOrderedMultiDict
    values = request.form
    for x, y in values.iteritems():
        arg += "&{x}={y}".format(x=x,y=y)

    validate_url = 'https://www.sandbox.paypal.com' \
                   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
                   .format(arg=arg)

    print 'Validating IPN using {url}'.format(url=validate_url)

    r = requests.get(validate_url)

    if r.text == 'VERIFIED':
        print "PayPal transaction was verified successfully."
        # Do something with the verified transaction details.
        payer_email =  request.form.get('payer_email')
        print "Pulled {email} from transaction".format(email=payer_email)
        payment_status = request.form.get('payment_status')
        if payment_status == 'Completed':
            receiver_email = request.form.get('receiver_email')
            if receiver_email == 'wangchenclark-facilitator@foxmail.com':
                mc_gross = float(request.form.get('mc_gross'))
                mc_currency = request.form.get('mc_currency')
                if mc_gross == 100 and mc_currency == 'USD':
                    #检验已经完成，可以更新订单状态了
                    order_id = int(request.form.get('item_number'))
                    order = Order.query.get(order_id)
                    order.status = 1
                    db.session.commit()
    else:
        print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

    return r.text

api.add_resource(OrderApi, '/api/v1/order', endpoint='order')
api.add_resource(OrderListApi, '/api/v1/orders', endpoint='orders')



