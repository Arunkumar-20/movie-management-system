from flask import Flask,render_template,request,session,jsonify
from db import db
from bson import ObjectId

def searching():
    if request.method == 'POST':
        name = request.form['name'].title()
        year = request.form['year']
        type = request.form['operater']
        if name:
            data = db.movies.find({"movie_name": name})
            return render_template("movies.html", data=data)
        if type == "lessthen":
            data = db.movies.find({"relese_date": {"$lte": year}})
            return render_template("movies.html", data=data)
        else:
            data = db.movies.find({"relese_date": {"$gte": year}})
            return render_template("movies.html", data=data)
    return render_template("find.html")

def user_recommended():
    if request.method == 'GET':
        user_name = session["name"]
        Genre = db.user_data.find_one({"name":user_name})
        movie_type = Genre["genre"]
        data = db.movies.find({"movie_type": movie_type})
        return render_template("movies.html", data=data)

def add_comments(movieid):
    if request.method == 'POST':
        comment = request.form['comments']
        db.movies.update_one({"_id": ObjectId(movieid)}, {"$push": {"comments": [session['name'], comment]}})
        return jsonify({"status": "comments added successfully"})
    return render_template("comments.html", id=movieid)