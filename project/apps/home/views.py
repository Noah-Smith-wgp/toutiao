from flask import session, request, abort
from flask_restful import Api, Resource

from project.apps.home import home_buleprint
from project.models.news import Channel, Article
from project.models.user import Relation

home_api = Api(home_buleprint)


from flask import make_response, current_app
from flask_restful.utils import PY3
from json import dumps


@home_api.representation('application/json')
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


class ChannelsResource(Resource):

    def get(self):

        channels = Channel.query.all()
        channel_list = []
        for channel in channels:
            channel_list.append({
                'id': channel.id,
                'name': channel.name
            })

        return {'channels': channel_list}


class IndexView(Resource):

    def get(self):

        channel_id = request.args.get('channel_id', 0)
        page = request.args.get('page', 1)
        per_page = request.args.get('per_page', 2)

        try:
            page = int(page)
            per_page = int(per_page)
        except Exception:
            page = 1
            per_page = 10

        if channel_id == 0:
            channel_id = 1

        page_articles = Article.query.filter_by(channel_id=channel_id, status=Article.STATUS.APPROVED).\
            paginate(page=page, per_page=per_page)

        results = []
        for item in page_articles.items:
            results.append({
                "art_id": item.id,
                "title": item.title,
                "aut_id": item.user.id,
                "pubdate": item.ctime.strftime('%Y-%m-%d %H:%M:%S'),
                "aut_name": item.user.name,
                "comm_count": item.comment_count
            })

        return {'per_page': per_page, 'results': results}


class DetailResource(Resource):

    def get(self, article_id):

        try:
            article = Article.query.get(article_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        else:
            # 完成是否关注
            is_followed = False
            if current_app.user_id:
                try:

                    user_id = current_app.user_id
                    target_user_id = article.user.id
                    relation = Relation.query.filter_by(user_id=user_id, target_user_id=target_user_id).first()
                except Exception as e:
                    current_app.logger.error(e)
                else:
                    is_followed = True

            # Todo 完成是否喜欢
            attitude = 1
            # Todo 判断是否收藏
            is_collected = False

            data = {
                "art_id": article.id,
                "title": article.title,
                "pubdate": article.ctime.strftime('%Y-%m-%d %H:%M:%S'),
                "aut_id": article.user.id,
                "aut_name": article.user.name,
                "aut_photo": article.user.profile_photo,
                "content": article.content.content,
                "is_followed": is_followed,
                "attitude": attitude,  # 不喜欢0 喜欢1 无态度-1
                "is_collected": is_collected
            }

            return data


home_api.add_resource(ChannelsResource, '/channels')
home_api.add_resource(IndexView, '/articles')
home_api.add_resource(DetailResource, '/articles/<article_id>/')
