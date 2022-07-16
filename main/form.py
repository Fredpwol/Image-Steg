from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Email
from flask_wtf.file import FileField, FileAllowed, FileRequired


class EncodeForm(FlaskForm):
    file = FileField(
                     validators=[
                         FileRequired(),
                         FileAllowed(["png", "jpg", "jpeg"], "Images Only!")
                     ])
    message = TextAreaField(description="Enter heidden message")
    message_file = FileField("Hidden Message")
    email = TextAreaField("Email",
                          validators=[Email("Please enter a valid email")])
    submit = SubmitField("Encode Image")


class DecodeForm(FlaskForm):
    file = FileField("Image File",
                     validators=[
                         FileRequired("Please Input a Image to decode"),
                         FileAllowed(["png", "jpg", "jpeg"], "Images Only!")
                     ])
    email = TextAreaField("Email",
                          validators=[Email("Please enter a valid email")])

    submit = SubmitField("Decode Image")
