import os
from flask_socketio import emit
from flask import url_for

from service import worker
from steg.algo import ImageParser, Format
from main import app


@worker.task
def encode_text_on_image(img_path, text, client_id):
    with app.app_context():
        img = ImageParser(img_path)

        for prog in img.encode(
            Format.TXT.value, text, as_generator=True, output_dir="static"
        ):
            emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        emit("encode:complete", {"data": encoded_image_url}, to=client_id)


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
            emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        emit("encode:complete", {"data": encoded_image_url}, to=client_id)


@worker.task
def encode_audio_on_image(img_path, audio_file, client_id):
    with app.app_context():
        img = ImageParser(img_path)

        ext = os.path.splitext(audio_file)[-1].lower()
        image_format = Format.WAV.value if ext == "wav" else Format.MP3.value

        for prog in img.encode(
            image_format, audio_file, as_generator=True, output_dir="static"
        ):
            emit("encode:progress", {"progress": prog}, to=client_id)

        filename = os.path.basename(img_path)[: img_path.find(".")]

        encoded_image_url = url_for("static", filename=filename, _external=True)

        emit("encode:complete", {"data": encoded_image_url}, to=client_id)

@worker.task
def test_func(n):
    res = []
    for i in range(1, n+1):
        for j in range(1, i // 2):
            if j * j == i:
                res.append(i)
                break
    print(res)

