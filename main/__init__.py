from flask import Flask
from main import config

app = Flask(__name__)
app.config.from_object(config.Development)

from main import routes