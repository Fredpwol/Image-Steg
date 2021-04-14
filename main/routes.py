from main import app

@app.route("/encode")
def encode_image():
    return "Encode Page!"

@app.route("/decode")
def decode_image():
    return "Decode Page!!"