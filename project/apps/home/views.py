from flask import session

from project.apps.home import home_buleprint


@home_buleprint.route('/')
def index():

    session['id'] = 'abc'
    return '--index--!!!'
