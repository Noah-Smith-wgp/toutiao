import re
from datetime import datetime
from flask_restful import Api, Resource, reqparse

from project import db
from project.apps.user import user_buleprint
from project.models.user import User
from project.utils.user import generate_token


# 使用api接管蓝图
user_api = Api(user_buleprint)

from flask import make_response, current_app
from flask_restful.utils import PY3
from json import dumps


@user_api.representation('application/json')
def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    if 'message' not in data:
        data = {
            'message': 'OK',
            'data': data
        }

    settings = current_app.config.get('RESTFUL_JSON', {})

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    if current_app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', not PY3)

    # always end the json dumps with a new line
    # see https://github.com/mitsuhiko/flask/pull/1262
    dumped = dumps(data, **settings) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp


class SmsCodeResource(Resource):

    def get(self, mobile):

        return {'mobile': mobile}


def check_mobile(value):

    if not re.match(r'1[3-9]\d{9}', value):
        raise ValueError('手机号不正确')
    return value


class LoginResource(Resource):

    def post(self):

        parser = reqparse.RequestParser()

        parser.add_argument('mobile', location='json', required=True, type=check_mobile)
        parser.add_argument('code', location='json', required=True)

        args = parser.parse_args()

        mobile = args.get('mobile')
        code = args.get('code')

        try:
            user = User.query.filter_by(mobile=mobile).first()
        except Exception as e:
            current_app.logger.error(e)

        if user:
            user.last_login = datetime.now()
            db.session.commit()
        else:
            user = User()
            user.mobile = mobile
            user.name = mobile
            user.last_login = datetime.now()

            db.session.add(user)
            db.session.commit()

        token = generate_token(user.id)

        return {'token': token}


user_api.add_resource(SmsCodeResource, '/sms/codes/<mobile>/')
user_api.add_resource(LoginResource, '/authorizations')
