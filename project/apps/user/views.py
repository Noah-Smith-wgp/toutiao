import random
import re
from datetime import datetime
from flask_restful import Api, Resource, reqparse

from project import db
from project.apps.user import user_buleprint
from project.libs.yuntongxun.ccp_sms import CCP
from project.models.news import UserChannel
from project.models.user import User, Relation
from project.utils.user import generate_token, check_user_token, loginrequired, generate_jwt_token

# 使用api接管蓝图
user_api = Api(user_buleprint)

from flask import make_response, current_app, request, g, abort, jsonify
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

        # token = generate_token(user.id)
        token, refresh_token = generate_jwt_token(user.id)

        # return {'token': token}
        return jsonify({'token': token, 'refresh_token': refresh_token}), 201


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
            user_channels = UserChannel.query.filter_by(user_id=user_id, is_deleted=False).all()
        except Exception as e:
            current_app.logger.error(e)

        channels = []
        for item in user_channels:
            channels.append({
                'id': item.id,
                'name': item.channel.name
            })

        return {'channels': channels}

    def put(self):

        user_id = g.user_id
        channels = request.json.get('channels')

        UserChannel.query.filter_by(user_id=user_id).update({'is_deleted': True})

        db.session.commit()

        for channel in channels:
            flag = UserChannel.query.filter_by(user_id=user_id, channel_id=channel.get('id')).\
                update({'sequence': channel.get('seq'), 'is_deleted': False})
            if flag:
                db.session.commit()
            else:
                new_channel = UserChannel()
                new_channel.user_id = user_id
                new_channel.channel_id = channel.get('id')
                new_channel.is_deleted = False
                new_channel.sequence = channel.get('seq')

                db.session.add(new_channel)
                db.session.commit()

        return {'channels': channels}


class FollowResource(Resource):

    method_decorators = [loginrequired]

    def post(self):

        user_id = g.user_id

        parse = reqparse.RequestParser()
        parse.add_argument('target', location='json', required=True)

        args = parse.parse_args()

        target = args.get('target')

        user = None
        try:
            user = User.query.get(target)
        except Exception as e:
            current_app.logger.error(e)

        if user is None:
            abort(404)

        relation = Relation()
        relation.user_id = user_id
        relation.target_user_id = target
        relation.relation = Relation.RELATION.FOLLOW

        try:
            db.session.add(relation)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return {'message': 'error', 'data': {}}

        return {'target': target}

    def get(self):

        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 10)
        user_id = g.user_id

        try:
            page = int(page)
            per_page = int(per_page)
        except Exception:
            page = 1
            per_page = 10

        relations_page = Relation.query.filter_by(user_id=user_id, relation=Relation.RELATION.FOLLOW).paginate(page=page, per_page=per_page)

        relation_list = []

        for item in relations_page.items:
            user = User.query.get(item.target_user_id)

            # 相互关注判断
            mutual_follow = False
            for relation in user.followings:
                if relation.target_user_id == user_id:
                    mutual_follow = True
                    break

            relation_list.append({
                "id": item.id,
                "name": user.name,
                "photo": user.profile_photo,
                "fans_count": user.fans_count,
                "mutual_follow": mutual_follow  # 是否为互相关注
            })

        return {
            "total_count": relations_page.total,
            "page": page,
            "per_page": per_page,
            "results": relation_list
        }


class FollowDeleteResource(Resource):

    method_decorators = [loginrequired]

    def delete(self, target):

        user_id = g.user_id

        try:
            relation = Relation.query.filter_by(user_id=user_id, target_user_id=target).first()
        except Exception as e:
            current_app.logger.error(e)
            abort(404)

        try:
            db.session.delete(relation)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)

        return {'message': 'OK'}


user_api.add_resource(SmsCodeResource, '/sms/codes/<mobile>/')
user_api.add_resource(LoginResource, '/authorizations')
user_api.add_resource(CenterResource, '/user')
user_api.add_resource(UserChannelResource, '/user/channels')
user_api.add_resource(FollowResource, '/user/followings')
user_api.add_resource(FollowDeleteResource, '/user/followings/<target>/')
