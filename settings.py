import os
from dotenv import load_dotenv
load_dotenv()

CELERY_MESSAGING_QUEUE = os.getenv("CELERY_MESSAGE_QUEUE")
SOCKET_IO_MESSAGING_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE")

ENCODE_INPUT_DIR = "main/static/image/temp/encode"
ENCODE_OUTPUT_DIR = "main/static/image/results/encoded"
DECODE_INPUT_DIR = "main/static/image/temp/decode"
DECODE_OUTPUT_DIR = "main/static/image/results/decoded"
