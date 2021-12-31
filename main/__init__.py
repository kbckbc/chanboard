# __init__ file will be executed when 'main' package loaded
from flask import Flask
from datetime import datetime
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
import time
import math

from flask import session
from datetime import timedelta

app = Flask(__name__)

# can use mongoDB conveniently using flask_pymongo
# to use flash() function of flask, need to set SECRET_KEY
# to set the session timeout
app.config["MONGO_URI"] = "mongodb://localhost:27017/chanboard"
app.config["SECRET_KEY"] = "abcdefg"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1)
mongo = PyMongo(app)

from main.common import login_required
from main.filter import format_datetime
from main import board
from main import member
