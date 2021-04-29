from flask import Blueprint, redirect, url_for

root = Blueprint('root', __name__, template_folder='../templates')

api = Blueprint('api', __name__, template_folder='../templates', url_prefix='/api/v1')
articles = Blueprint('articles', __name__, template_folder='../templates', url_prefix='/articles')
auth = Blueprint('auth', __name__, template_folder='../templates', url_prefix='/auth')
exchanges = Blueprint('exchanges', __name__, template_folder='../templates', url_prefix='/exchanges')
indexes = Blueprint('indexes', __name__, template_folder='../templates', url_prefix='/indexes')
marketstack = Blueprint('marketstack', __name__, template_folder='../templates', url_prefix='/marketstack')
profile = Blueprint('profile', __name__, template_folder='../templates', url_prefix='/profile')
opinions = Blueprint('opinions', __name__, template_folder='../templates', url_prefix='/opinions')


@root.route('/')
def redirect_to_indexes():
    return redirect(url_for('indexes.get_indexes'))
