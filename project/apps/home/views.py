from flask import session
from flask_restful import Api, Resource

from project.apps.home import home_buleprint


home_api = Api(home_buleprint)


# @home_buleprint.route('/')
# def index():
#
#     session['id'] = 'abc'
#     return '--index--!!!'


class IndexView(Resource):

    def get(self):

        return {'msg': 'index'}


home_api.add_resource(IndexView, '/')
