import os
from main import app
from flask import request, flash, redirect, render_template


from main.form import EncodeForm, DecodeForm
from werkzeug.utils import secure_filename


@app.before_first_request
def check_image_path():
    if not os.path.exists(os.path.join(app.root_path, "images")):
        os.mkdir(os.path.join(app.root_path, "images"))

@app.route("/", methods=["GET", "POST"])
def home():
    form = EncodeForm(request.form)
    deform = DecodeForm(request.form)
    return render_template("base.html", encode_form=form, decode_form = deform)

@app.route("/encode", methods=["GET", "POST"])
def encode_image():
    form = EncodeForm()
    if form.validate_on_submit():
        return redirect("home")
    return "Encode!!"

@app.route("/decode")
def decode_image():
    form = DecodeForm
    return render_template('decode.html', form=form, title = 'Decode Form' )


@app.route('/encode-image', methods=['POST'])
def encode():
    from service.tasks import encode_text_on_image

    data = request.form

    f = request.files.get('file')
    img_path = f'main/static/image/temp/encode/{f.filename}'
    f.save(img_path)
    payload = data.get("message")
    client_id = data.get("client_id")
    
    encode_text_on_image.delay(img_path, payload, client_id)
    return {"status": "Success"}, 201
