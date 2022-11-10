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
    encode_form = EncodeForm()
    decode_form = DecodeForm()
    
    #if form.validate_on_submit():
    #    pass
        
    
    #if request.method.lower() == "post":
        #print(form.is_submitted(), "submitted", form.validate(),)
        #print ("Submitted!!")
    if encode_form.validate_on_submit():
        encode_f = encode_form.file.data
        print(encode_f)
        filename = secure_filename(encode_f.filename)
        print("Path", os.path.join(app.root_path, "images", filename))
        encode_f.save()
        return redirect("/encode")
    if decode_form.validate_on_submit():
        decode_f = decode_form.file.data
        filename = secure_filename(decode_f.filename)
        print(request.files)
        decode_f.save()
        

    return render_template("base.html", encode_form=encode_form, decode_form = decode_form)

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