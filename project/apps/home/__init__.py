from flask import Blueprint

home_buleprint = Blueprint('home', __name__)

from . import views
