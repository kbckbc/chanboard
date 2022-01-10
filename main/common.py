# to use decorator for kick out users having no session value
from functools import wraps
from main import session, redirect, request, url_for, ALLOWED_EXTENSIONS
from string import ascii_lowercase, ascii_uppercase, digits
import random

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password)


def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


def rand_generator(length=8):
    char = ascii_lowercase + ascii_uppercase + digits
    return "".join(random.sample(char, length))



# this is decorator to check whether login or not
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None or session.get("id") == "":
            # The reason for next_url is going back to exact same page after login
            return redirect(url_for("member_login", next_url=request.url))
        return f(*args, **kwargs)
    return decorated_function