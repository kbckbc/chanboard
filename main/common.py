# to use decorator for kick out users having no session value
from functools import wraps
from main import session, redirect, request, url_for

# this is decorator to check whether login or not
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None or session.get("id") == "":
            # The reason for next_url is going back to exact same page after login
            return redirect(url_for("member_login", next_url=request.url))
        return f(*args, **kwargs)
    return decorated_function