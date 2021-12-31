from main import *


@app.route("/list")
def board_list():
    board = mongo.db.board

    # search variables
    searchType = request.args.get("searchType", 0, type=int)
    searchKeyword = request.args.get("searchKeyword", "", type=str)

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
    row = list(board.find(query).sort("date", -1).skip((pagePos-1) * pageLimit).limit(pageLimit))
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
@login_required
def board_view(idx):
    # Getting a value from 'request' instance of flask
    # GET : request.args.get
    #   idx = request.args.get("idx")
    # POST : request.form.get
    if idx is not None:
        board = mongo.db.board
        # when searching with an id, need to convert an id into ObjectId
        # need to import bson.objectid
        data = board.find_one({"_id": ObjectId(idx)})

        # return_document=True : return the date after update reflection
        # return_document=False: return the data before update reflection
        data = board.find_one_and_update(
            {"_id": ObjectId(idx)},
            {"$inc": {"view": 1}},
            return_document=True,
        )

        if data is not None:
            result = {
                "_id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "date": data.get("date"),
                "view": data.get("view"),
                "writer_id": data.get("writer_id", "")
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
@login_required
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
            "writer_id": session.get("id"),
            "view": 0
        }
        row = board.insert_one(post)
        return redirect(url_for("board_view", idx=row.inserted_id))

    else:
        # render_template is from flask
        # It will find a file in the templates folder
        return render_template("write.html")

@app.route("/edit/<idx>", methods=["GET", "POST"])
def board_edit(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)})
    if data is None:
        flash("There's no such a post")
        return redirect(url_for('board_list'))
    else:
        if session.get("id") == data.get("writer_id"):
            if request.method == "GET":
                return render_template("edit.html", data=data)
            else:
                title = request.form.get("title")
                contents = request.form.get("contents")

                board.update_one({"_id": ObjectId(idx)}, {
                    "$set": {
                        "title": title,
                        "contents": contents
                    }
                })
                return redirect(url_for("board_view", idx=idx))
        else:
            flash("No right to edit the post.")
            return redirect(url_for("board_list"))


@app.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)})
    if data.get("writer_id") == session.get("id"):
        board.delete_one({"_id": ObjectId(idx)})
        flash("The post has been deleted")
    else:
        flash("No right to delete the post")
    return redirect(url_for("board_list"))

