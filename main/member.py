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
            return render_template("join.html", title="Sign up for a member")

        if password1 != password2:
            flash("Password don't match. Try again.")
            return render_template("join.html", title="Sign up for a member")

        members = mongo.db.members
        currTime = round(datetime.utcnow().timestamp() * 1000)

        cnt = len(list(members.find({"email": email})))
        if cnt > 0:
            flash("Input email already exists! Use different email address.")
            return render_template("join.html", title="Sign up for a member")
        
        post = {
            "name": name,
            "email": email,
            "password": hash_password(password2),
            "joindate": currTime,
            "logintime": "",
            "logincount": 0,
        }

        members.insert_one(post)

        return redirect(url_for("member_login"))
    else:
        return render_template("join.html", title="Sign up for a member")


@app.route("/login", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        next_url = request.form.get("next_url")


        print("aaa", email, password, next_url)

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
            print("bbb", data.get("password"), password)
            print("ccc", check_password(data.get("password"), password))

            if check_password(data.get("password"), password):
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
        return render_template("login.html", next_url=next_url, title="Log in")


@app.route("/logout")
def member_logout():
    del session["name"]
    del session["id"]
    del session["email"]
    return redirect(url_for('member_login'))