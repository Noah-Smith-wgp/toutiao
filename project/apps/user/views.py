from project.apps.user import user_buleprint


@user_buleprint.route('/login')
def login():
    return {'msg': 'OK'}
