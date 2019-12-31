from project.apps.user import user_buleprint
from flask_restful import Api, Resource


# 使用api接管蓝图
user_api = Api(user_buleprint)


# @user_buleprint.route('/login')
# def login():
#     return {'msg': 'OK'}

class LoginView(Resource):

    def get(self):

        return {'msg': 'OK kakakak'}


user_api.add_resource(LoginView, '/login')
