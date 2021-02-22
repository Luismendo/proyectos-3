from flask import Blueprint

root = Blueprint('root', __name__, template_folder='../templates')

articles = Blueprint('articles', __name__, template_folder='../templates', url_prefix='/articles')
auth = Blueprint('auth', __name__, template_folder='../templates', url_prefix='/auth')
indexes = Blueprint('indexes', __name__, template_folder='../templates', url_prefix='/indexes')
marketstack = Blueprint('marketstack', __name__, template_folder='../templates', url_prefix='/marketstack')
profile = Blueprint('profile', __name__, template_folder='../templates', url_prefix='/profile')
