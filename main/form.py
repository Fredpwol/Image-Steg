from flask_wtf import FlaskForm
from wtforms import TextAreaField, TextField
from wtforms.validators import Email
from flask_wtf.file import FileField, FileAllowed, FileRequired

class EncodeForm(FlaskForm):
    file = FileField("Image File", validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "Images Only!")])
    message = TextAreaField("Message")
    message_file = FileField("Hidden Message"])
    email = TextAreaField("Email", validators=[Email("Please enter a valid email")])



class DecodeForm(FlaskForm):
    file = FileField("Image File", validators=[FileRequired("Please Input a Image to decode"), FileAllowed(["png", "jpg", "jpeg"], "Images Only!")])
    email = TextAreaField("Email", validators=[Email("Please enter a valid email")])
