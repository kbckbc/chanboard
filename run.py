import requests
from datetime import datetime
from flask import Flask
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

app = Flask(__name__)
# can use mongoDB conveniently using flask_pymongo
app.config["MONGO_URI"] = "mongodb://localhost:27017/chanboard"
app.config["SECRET_KEY"] = "abcdefg"
mongo = PyMongo(app)


# To show using jinja template filter fucntion
@app.template_filter("formatdatetime")
def format_datetime(value):
    if value is None:
        return ""

    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    value = datetime.fromtimestamp(int(value) / 1000) + offset
    return value.strftime('%Y-%m-%d %H:%M:%S')

@app.route("/list")
def board_list():
    board = mongo.db.board

    # search variables
    searchType = request.args.get("searchType", 0, type=int)
    searchKeyword = request.args.get("searchKeyword", '', type=str)

    query = {}
    searchKeywordList = []
    if searchType == 0:
        searchKeywordList.append({"title": {"$regex": searchKeyword}})
        searchKeywordList.append({"contents": {"$regex": searchKeyword}})
        searchKeywordList.append({"name": {"$regex": searchKeyword}})
    elif searchType == 1:
        searchKeywordList.append({"title": {"$regex": searchKeyword, "$options":"i"}})
    elif searchType == 2:
        searchKeywordList.append({"contents": {"$regex": searchKeyword}})
    elif searchType == 3:
        searchKeywordList.append({"title": {"$regex": searchKeyword}})
        searchKeywordList.append({"contents": {"$regex": searchKeyword}})
    elif searchType == 4:
        searchKeywordList.append({"name": {"$regex": searchKeyword}})

    if len(searchKeywordList) > 0:
        query = {"$or": searchKeywordList}

    print(query)

    # definition of paging variables
    pagePos = request.args.get("pagePos", 1, type=int)
    pageLimit = request.args.get("pageLimit", 7, type=int)

    # Getting limited pages from the start page variable 
    row = list(board.find(query).skip((pagePos-1) * pageLimit).limit(pageLimit))
    count = len(list(board.find(query)))
    lastPage = math.ceil(count / pageLimit)
    blockSize = 5
    blockPos = int((pagePos - 1) / blockSize)
    blockStartPos = (blockPos * blockSize) + 1
    blockLastPos = blockStartPos + (blockSize -1)
    print(count, pageLimit, lastPage, blockPos, blockStartPos, blockLastPos,)

    # Variables paging
    # blockSize
    # blockStart ..
    # blockLast
    # lastPage

    return render_template(
        "list.html",
        data=row,
        dataCount=count,
        pagePos=pagePos,
        blockStartPos=blockStartPos,
        blockLastPos=blockLastPos,
        lastPage=lastPage,
        pageLimit=pageLimit,
        searchType=searchType,
        searchKeyword=searchKeyword
        )
    
# <idx> is for clean URL
# when using clean URL, there will be no parameter in the URL
# Type <idx> in the route and function definition.
@app.route("/view/<idx>")
def board_view(idx):
    # Getting a value from 'request' instance of flask
    # GET : request.args.get
    #   idx = request.args.get("idx")
    # POST : request.form.get
    if idx is not None:
        board = mongo.db.board
        # when searching with an id, need to convert an id into ObjectID
        # need to import bson.objectid
        data = board.find_one({"_id": ObjectId(idx)})

        if data is not None:
            result = {
                "_id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "date": data.get("date"),
                "view": data.get("view"),
            }

            # search variables
            pagePos = request.args.get("pagePos", 1, type=int)

            searchType = request.args.get("searchType", 0, type=int)
            searchKeyword = request.args.get("searchKeyword", '', type=str)


            # render_template is from flask
            # It will find a file in the templates folder
            return render_template("view.html", result=result, searchType=searchType, searchKeyword=searchKeyword, pagePos=pagePos)
    # abort func is from flask
    return abort(400)


@app.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "POST":
        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")

        currTime = round(datetime.utcnow().timestamp() * 1000)
        board = mongo.db.board
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "date": currTime,
            "view": 0
        }
        row = board.insert_one(post)
        return redirect(url_for("board_view", idx=row.inserted_id))

    else:
        # render_template is from flask
        # It will find a file in the templates folder
        return render_template("write.html")


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


if __name__ == "__main__":
    app.run(debug=True)
