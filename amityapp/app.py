import flask
import random
import requests

from rich import print
from flask_socketio import SocketIO, emit

app = flask.Flask(__name__)

METHODS = ['GET', 'POST', 'PUT', 'DELETE']
API_VERSION = 'v10'

app.config['SECRET_KEY'] = str(random.getrandbits(256))

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')

def get_own_info(*args, **kwargs) -> dict:
    return {
        'username': 'testuser',
        'name': 'Test User',
        'description': 'Example text',
        'id': 1234567890,
        'discriminator': '0001',
        'avatar': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'icon': 'https://cdn.discordapp.com/embed/avatars/0.png',
        'bot_public': True,
        'bot_require_code_grant': False,
        'owner': {
            'username': 'testuser',
            'discriminator': '0001',
            'id': 1234567890,
            'avatar': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        },
        'verify_key': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    }

def get_request_info(request) -> dict:
    return {
        'method': request.method,
        'path': request.path,
        'args': request.args or None,
        'form': request.form or None,
        'headers': request.headers
    }

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/<path:path>', methods=METHODS)
def show(path):
    print(get_request_info(flask.request))
    return flask.Response(status=404)

@app.route('/gateway/<path:path>', methods=METHODS)
def gateway():
    print(get_request_info(flask.request))

    resp = requests.request(
        method=flask.request.method,
        url=f'https://gateway.discord.gg/{path}',
        headers=flask.request.headers,
        data=flask.request.data
    )

    print({
        'status_code': resp.status_code,
        'headers': resp.headers,
        'text': resp.text
    })

    return flask.Response(
        status=resp.status_code,
        headers=resp.headers,
        response=resp.text
    )

@app.route(f'/api/{API_VERSION}/users/@me')
def api_users_me():
    return get_own_info(flask.request)

@app.route(f'/api/{API_VERSION}/oauth2/applications/@me')
def api_oauth2_applications_me():
    return get_own_info(flask.request)



app.run(port=4455, debug=True, use_evalex=False)
