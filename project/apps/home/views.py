from flask import Blueprint, session

home_buleprint = Blueprint('home', __name__)


@home_buleprint.route('/')
def index():

    session['id'] = 'abc'
    return '--index--'
