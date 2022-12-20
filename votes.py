from flask import Flask,request,render_template,session,jsonify
from bson import ObjectId
from db import db

def votes(movieid):
    if request.method == 'POST':
        vote_type = request.form['vote']
        user = session['name']
        movies = db.movies.find_one({"_id":ObjectId(movieid)})
        upvote = movies['upvote']
        downvote = movies['downvote']
        user_name = db.user_data.find_one({"name": user})

        if vote_type == "upvote":
            if user_name.get(movieid)is None:
                up_vote = upvote + 1
                db.movies.update_one({"_id":ObjectId(movieid)}, {"$set": {"upvote": up_vote}})
                db.user_data.update_one({"name": user}, {"$set": {str(movieid): 1}})
                return jsonify({"status":"upvote added successfully"})

        if vote_type == "downvote":
            if user_name.get(movieid)is None:
                down_vote = downvote + 1
                db.movies.update_one({"_id":ObjectId(movieid)}, {"$set": {"downvote": down_vote}})
                db.user_data.update_one({"name": user}, {"$set": {str(movieid): 2}})
                return jsonify({"status":"downvote added successfully"})

        if vote_type == "downvote":
            if user_name[str(movieid)] == 1:
                up_vote = upvote - 1
                down_vote = downvote + 1
                db.movies.update_one({"_id":ObjectId(movieid)}, {"$set": {"downvote": down_vote,"upvote": up_vote}})
                db.user_data.update_one({"name": user}, {"$set": {str(movieid): 2}})
                return jsonify({"status":"downvote added successfully"})
            if user_name[str(movieid)] == 2:
                return jsonify({"status":"you are allready downvoted"})

        if vote_type == "upvote":
            if user_name[str(movieid)] == 2:
                up_vote = upvote + 1
                down_vote = downvote - 1
                db.movies.update_many({"_id":ObjectId(movieid)}, {"$set": {"downvote": down_vote, "upvote": up_vote}})
                db.user_data.update_one({"name": user}, {"$set": {str(movieid): 1}})
                return jsonify({"status":"upvote added successfully"})
            if user_name[str(movieid)] == 1:
                return jsonify({"status":"you are allready upvoted"})

    return render_template("vote.html",id = movieid)