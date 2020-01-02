from flask import Blueprint

home_buleprint = Blueprint('home', __name__, url_prefix='/app/v1_0')

from . import views
