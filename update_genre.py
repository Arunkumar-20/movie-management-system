from flask import Flask,render_template,jsonify,request,session
from db import db

def update_genre():
    if request.method == 'POST':
        type = request.form['gener']
        name = session['name']
        db.user_data.update_one({"name":name},{"$set":{"genre":type}})
        return jsonify({"status":"Genre updated successfully"})
    return render_template("genre.html")