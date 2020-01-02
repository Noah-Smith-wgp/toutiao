from flask import session, request
from flask_restful import Api, Resource

from project.apps.home import home_buleprint
from project.models.news import Channel, Article

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


home_api.add_resource(ChannelsResource, '/channels')
home_api.add_resource(IndexView, '/articles')
