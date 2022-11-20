import os
from flask_socketio import emit, SocketIO
from flask import url_for
from settings import SOCKET_IO_MESSAGING_QUEUE

from service import worker
from steg.algo import ImageParser, Format
from main import app


socketio = SocketIO(message_queue=SOCKET_IO_MESSAGING_QUEUE)


@worker.task
def encode_text_on_image(img_path, text, client_id):
    with app.app_context(), app.test_request_context():
        img = ImageParser(img_path)

        for prog in img.encode(
            Format.TXT.value, text, as_generator=True,
        ):
            socketio.emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        socketio.emit("encode:complete", {"data": encoded_image_url}, to=client_id)


@worker.task
def encode_image_on_image(img_path, img, client_id):
    with app.app_context():
        img = ImageParser(img_path)

        ext = os.path.splitext(img)[-1].lower()
        image_format = (
            Format.JPG.value if ext == "jpg" or ext == "jpeg" else Format.PNG.value
        )

        for prog in img.encode(
            image_format, img, as_generator=True, output_dir="static"
        ):
            socketio.emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        socketio.emit("encode:complete", {"data": encoded_image_url}, to=client_id)


@worker.task
def encode_audio_on_image(img_path, audio_file, client_id):
    with app.app_context():
        img = ImageParser(img_path)

        ext = os.path.splitext(audio_file)[-1].lower()
        image_format = Format.WAV.value if ext == "wav" else Format.MP3.value

        for prog in img.encode(
            image_format, audio_file, as_generator=True, output_dir="static"
        ):
            socketio.emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        socketio.emit("encode:complete", {"data": encoded_image_url}, to=client_id)
