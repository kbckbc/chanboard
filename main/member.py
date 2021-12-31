from main import *

@app.route("/join", methods=["GET", "POST"])
def member_join():
    if request.method == "POST":
        name = request.form.get("name", type=str)
        email = request.form.get("email", type=str)
        password1 = request.form.get("password1", type=str)
        password2 = request.form.get("password2", type=str)

        if name == "" or email == "" or password1 == "" or password2 == "":
            flash("Check input again.")
            return render_template("join.html")

        if password1 != password2:
            flash("Password don't match. Try again.")
            return render_template("join.html")

        members = mongo.db.members
        currTime = round(datetime.utcnow().timestamp() * 1000)

        cnt = len(list(members.find({"email": email})))
        if cnt > 0:
            flash("Input email already exists! Use different email address.")
            return render_template("join.html")
        
        post = {
            "name": name,
            "email": email,
            "password": password2,
            "joindate": currTime,
            "logintime": "",
            "logincount": 0,
        }

        members.insert_one(post)

        return ""
    else:
        return render_template("join.html")


@app.route("/login", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")
        next_url = request.form.get("next_url")

        members = mongo.db.members
        data = members.find_one({"email": email})

        if data is None:
            flash("There's no id")
            return redirect(url_for("member_login"))
        else:
            '''
                session is stored in a server side
                In permanent mode, session timeout can be managed
            '''
            if data.get("pass") == password:
                session["email"] = email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                session.permanent = True

                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect(url_for("board_list"))
            else:
                flash("There's no id")
                return redirect(url_for("member_login"))
    else:
        next_url = request.args.get("next_url", type=str)
        return render_template("login.html", next_url=next_url)
