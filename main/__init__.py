from flask import Flask
from main import config
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(config.Development)


from main import routes