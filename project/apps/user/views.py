import random
import re
from datetime import datetime
from flask_restful import Api, Resource, reqparse

from project import db
from project.apps.user import user_buleprint
from project.libs.yuntongxun.ccp_sms import CCP
from project.models.news import UserChannel
from project.models.user import User
from project.utils.user import generate_token, check_user_token, loginrequired


# 使用api接管蓝图
user_api = Api(user_buleprint)

from flask import make_response, current_app, request, g
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

        # 提取发送短信的标记 60秒避免频繁请求短信验证码
        send_flag = current_app.redis_store.get('send_flag_%s' % mobile)
        # 判断发送短信的标记是否存在（如果存在：频繁发送短信。反之，频率正常）
        if send_flag:
            return {'errmsg': '发送短信过于频繁'}

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        current_app.logger.info(sms_code)

        current_app.redis_store.setex('sms_%s' % mobile, 60, sms_code)
        current_app.redis_store.setex('send_flag_%s' % mobile, 60, 1)

        # 发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, 1], 1)

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
        current_app.logger.info(code)

        # 验证短信验证码
        # sms_code = current_app.redis_store.get('sms_%s' % mobile)
        # if code != sms_code:
        #     return {'msg': '手机验证码错误'}

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


class CenterResource(Resource):

    method_decorators = [loginrequired]

    def get(self):

        try:
            user = User.query.get(g.user_id)
        except Exception as e:
            current_app.logger.error(e)
        else:
            return {
                "id": user.id,
                "name": user.name,
                "photo": user.profile_photo,
                "intro": user.introduction,
                "art_count": user.article_count,
                "follow_count": user.following_count,
                "fans_count": user.fans_count
            }


class UserChannelResource(Resource):

    method_decorators = [loginrequired]

    def get(self):

        user_id = g.user_id

        try:
            user_channels = UserChannel.query.filter_by(user_id=user_id).all()
        except Exception as e:
            current_app.logger.error(e)

        channels = []
        for item in user_channels:
            channels.append({
                'id': item.id,
                'name': item.channel.name
            })

        return {'channels': channels}


user_api.add_resource(SmsCodeResource, '/sms/codes/<mobile>/')
user_api.add_resource(LoginResource, '/authorizations')
user_api.add_resource(CenterResource, '/user')
user_api.add_resource(UserChannelResource, '/user/channels')
