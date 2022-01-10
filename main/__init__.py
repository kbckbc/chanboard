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
from flask_wtf.csrf import CSRFProtect
import time
import math
import os

from flask import session
from datetime import timedelta

app = Flask(__name__)
csrf = CSRFProtect(app)

# can use mongoDB conveniently using flask_pymongo
# to use flash() function of flask, need to set SECRET_KEY
# to set the session timeout
app.config["MONGO_URI"] = "mongodb://localhost:27017/chanboard"
app.config["SECRET_KEY"] = "abcdefg"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=2)
mongo = PyMongo(app)


ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])
BOARD_IMAGE_PATH = "d:\\kbckbc\\images"
BOARD_ATTACH_FILE_PATH = "d:\\kbckbc\\uploads"
app.config["BOARD_IMAGE_PATH"] = BOARD_IMAGE_PATH
app.config["BOARD_ATTACH_FILE_PATH"] = BOARD_ATTACH_FILE_PATH
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024 # up to 15 MB

if not os.path.exists(app.config["BOARD_IMAGE_PATH"]):
    os.mkdir(app.config["BOARD_IMAGE_PATH"])
if not os.path.exists(app.config["BOARD_ATTACH_FILE_PATH"]):
    os.mkdir(app.config["BOARD_ATTACH_FILE_PATH"])

from main.common import login_required, allowed_file, rand_generator, hash_password, check_password
from main.filter import format_datetime
from main import board
from main import member
