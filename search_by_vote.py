from flask import Flask,render_template,request
from db import db
def search_by_vote():
    if request.method == 'POST':
        vote = request.form['vote']
        compare = request.form['type']
        if vote == 'upvote' and compare == 'Ascending':
            data = db.movies.find().sort(vote, 1)
            return render_template("movies.html", data=data)

        if vote == 'upvote' and compare == 'Desending':
            data = db.movies.find().sort(vote, -1)
            return render_template("movies.html", data=data)

        if vote == 'downvote' and compare == "Ascending":
            data = db.movies.find().sort(vote, 1)
            return render_template("movies.html", data=data)

        if vote == 'downvote' and compare == "Desending":
            data = db.movies.find().sort(vote, -1)
            return render_template("movies.html", data=data)
    return render_template("search.html")