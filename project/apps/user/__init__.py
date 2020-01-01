from flask import Blueprint

user_buleprint = Blueprint('user', __name__, url_prefix='/app/v1_0')

from . import views
