from flask import Flask
from main import config
from flask_socketio import SocketIO


app = Flask(__name__)

app.config.from_object(config.Development)
io = SocketIO(app)

from main import routes
from service import io_listeners
