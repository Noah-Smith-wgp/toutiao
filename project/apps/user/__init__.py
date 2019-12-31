from flask import Blueprint

user_buleprint = Blueprint('user', __name__)

from . import views
