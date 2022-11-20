from flask import Flask
from main import config
from flask_socketio import SocketIO
from settings import CELERY_MESSAGING_QUEUE, SOCKET_IO_MESSAGING_QUEUE


app = Flask(__name__)

app.config.from_object(config.Development)

io = SocketIO(app, message_queue=SOCKET_IO_MESSAGING_QUEUE, async_mode="gevent")

from main import routes
from service import io_listeners
