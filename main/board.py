from werkzeug.utils import secure_filename
from main import *
from flask import send_from_directory


def board_delete_attach_file(filename):
    abs_path = os.path.join(app.config["BOARD_ATTACH_FILE_PATH"], filename)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return True
    return False
    

@app.route("/comment_edit", methods=["POST"])
@login_required
def board_comment_edit():
    if request.method == "POST":
        idx = request.form.get("_id")
        new_comment = request.form.get("new_comment")

        comment = mongo.db.comment
        data = comment.find_one({"_id": ObjectId(idx)})
        if data.get("writer_id") == session.get("id"):
            comment.update_one(
                {"_id": ObjectId(idx)},
                {"$set": {"comment": new_comment}},
            )
            return jsonify(error="success")
        else:
            return jsonify(error="error")
    return abort(401)


@app.route("/comment_delete", methods=["POST"])
@login_required
def board_comment_delete():
    if request.method == "POST":
        idx = request.form.get("_id")
        comment = mongo.db.comment
        data = comment.find_one({"_id": ObjectId(idx)})
        if data.get("writer_id") == session.get("id"):
            comment.delete_one({"_id": ObjectId(idx)})
            return jsonify(error="success")
        else:
            return jsonify(error="error")
    return abort(401)


@app.route("/comment_list/<root_idx>", methods=["GET"])
@login_required
def board_comment_list_ajax(root_idx):
    comments = mongo.db.comment.find({"root_idx": root_idx}).sort("pubdate",-1)
    comments_list = []

    for c in comments:
        owner = True if c.get("writer_id") == session.get("id") else False

        comments_list.append({
            "_id": str(c.get("_id")),
            "root_idx": c.get("root_idx"),
            "name": c.get("name"),
            "writer_id": c.get("writer_id"),
            "comment": c.get("comment"),
            "pubdate": format_datetime(c.get("pubdate")),
            "owner": owner,
        })
    return jsonify(error="success", comment_lists=comments_list)


@app.route("/comment_write", methods=["POST"])
@login_required
def board_comment_write():
    if request.method == "POST":
        name = session.get("name")
        writer_id = session.get("id")
        root_idx = request.form.get("root_idx")
        comment = request.form.get("comment")
        current_utc_time = round(datetime.utcnow().timestamp()*1000)

        db = mongo.db.comment

        post = {
            "root_idx": str(root_idx),
            "writer_id": writer_id,
            "name": name,
            "comment": comment,
            "pubdate": current_utc_time
        }
        db.insert_one(post)
        return redirect(url_for("board_view", idx=root_idx))
        


@app.route("/upload_image", methods=["POST"])
def board_upload_image():
    if request.method == "POST":
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = "{}.jpg".format(rand_generator())
            savefilepath = os.path.join(app.config["BOARD_IMAGE_PATH"], filename)
            file.save(savefilepath)
            return url_for("board_image", filename=filename)


@app.route("/image/<filename>")
def board_image(filename):
    return send_from_directory(app.config["BOARD_IMAGE_PATH"], filename)


@app.route("/file/<filename>")
def board_file(filename):
    return send_from_directory(app.config["BOARD_ATTACH_FILE_PATH"], filename, as_attachment=True)

@app.route("/")
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
        searchKeyword=searchKeyword,
        title="Board list"
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
                "writer_id": data.get("writer_id", ""),
                "attachfile": data.get("attachfile", "")
            }

            # search variables
            pagePos = request.args.get("pagePos", 1, type=int)

            searchType = request.args.get("searchType", 0, type=int)
            searchKeyword = request.args.get("searchKeyword", '', type=str)

            # render_template is from flask
            # It will find a file in the templates folder
            return render_template("view.html", result=result, searchType=searchType, searchKeyword=searchKeyword, pagePos=pagePos, title="View a post detail")
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

        filename = None
        if "attachfile" in request.files:
            file = request.files["attachfile"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = "{}_{}.{}".format(filename.rsplit('.', 1)[0], currTime, filename.rsplit('.', 1)[1])
                file.save(os.path.join(app.config['BOARD_ATTACH_FILE_PATH'], filename))

        board = mongo.db.board
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "date": currTime,
            "writer_id": session.get("id"),
            "view": 0
        }
        if filename is not None:
            post["attachfile"] = filename

        row = board.insert_one(post)
        return redirect(url_for("board_view", idx=row.inserted_id))

    else:
        # render_template is from flask
        # It will find a file in the templates folder
        return render_template("write.html",title="Write a post")

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
                return render_template("edit.html", result=data, title="Edit a post")
            else:
                title = request.form.get("title")
                contents = request.form.get("contents")
                deletefile = request.form.get("deletefile","")
                
                if deletefile == "on" and data.get("attachfile"):
                    board_delete_attach_file(data.get("attachfile"))
                    
                filename = None
                currTime = round(datetime.utcnow().timestamp() * 1000)
                if "attachfile" in request.files:
                    file = request.files["attachfile"]
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = "{}_{}.{}".format(filename.rsplit('.', 1)[0], currTime, filename.rsplit('.', 1)[1])
                        file.save(os.path.join(app.config["BOARD_ATTACH_FILE_PATH"], filename))

                board.update_one({"_id": ObjectId(idx)}, {
                    "$set": {
                        "title": title,
                        "contents": contents,
                        "attachfile": filename
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

