from main import app
from flask import request, flash, redirect, render_template
from main.form import EncodeForm, DecodeForm

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encode", methods=["GET", "POST"])
def encode_image():
    form = EncodeForm()
    if form.validate_on_submit():
        return redirect("home")
    return "Encode!!"

@app.route("/decode")
def decode_image():
    return "Decode Page!!"
