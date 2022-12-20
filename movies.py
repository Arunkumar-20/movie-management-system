from flask import Flask,render_template,request,jsonify,redirect,session
from db import db
from bson import ObjectId

def add_movie():
    if request.method == 'POST':
        movie_name = request.form['movie_name'].title()
        date = request.form['date']
        type = request.form['type']
        db.movies.insert_one({"movie_name": movie_name, "relese_date": date, "movie_type": type, "upvote":0, "downvote":0})
        return jsonify({"status": "movie insertes sucessfully"})
    return render_template("addmovie.html")

def edit_movie(movieid):
    if request.method == 'POST':
        name = request.form['movie_name'].title()
        date = request.form['date']
        type = request.form['type']
        db.movies.update_one({"_id":ObjectId(movieid)},{"$set":{"movie_name":name,"relese_date":date,"movie_type":type}})
        return jsonify({"status": "movie updated sucessfully"})
    return render_template("editmovie.html",id = movieid)

def delete_movie(movieid):
    movie = db.movies.find_one({"_id": ObjectId(movieid)})
    _id = str(movie["_id"])
    db.movies.delete_one({"_id": ObjectId(movieid)})
    db.user_data.update_many({}, {'$unset': {_id: {'$lte': 2}}})
    return jsonify({"status": "movie deleted sucessfully"})