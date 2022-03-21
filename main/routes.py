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
    context = {"form" : form}
    if request.method.lower() == "post":
        print(form.is_submitted(), "submitted", form.validate(),)
        # print ("Submitted!!")
        # f = form.file.data
        # filename = secure_filename(f.filename)
        # print("Path", os.path.join(app.root_path, "images", filename))
        # return redirect("/")
        # f.save()
    return render_template("index.html", **context)

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