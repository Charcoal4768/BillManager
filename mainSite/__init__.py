from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_socketio import join_room, leave_room, send, emit
from dotenv import load_dotenv
from .utils import slugify, split
from .extensions import db, login_manager, migrate, csrf, socket
from .models import User
from .routes.api import api_bp
from .routes.views import views_bp
from .routes.auth import auth_bp
from werkzeug.middleware.proxy_fix import ProxyFix
import os

load_dotenv()
database_url = os.getenv('SQLALCHEMY_DATABASE_URI')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = not app.debug and not app.testing
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.jinja_env.filters['slugify'] = slugify
app.jinja_env.filters['split'] = split
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(views_bp)

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
csrf.init_app(app)
socket.init_app(app, cors_allowed_origins="*", async_mode='threading')

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception as e:
        return None
    
@app.errorhandler(Exception)
def handle_exception(error):
    print(error, Exception)
    return render_template('errors.html', error=error), 500

@socket.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    socket.emit('message', {'msg': f'User has joined the room: {room}'}, room=room)