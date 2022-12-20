from flask import Flask,render_template,session
from config import app
from db import db

def user_profile():
    name = session['name']
    data = db.user_data.find_one({"name":name})
    user_name = data['name']
    gmail = data['mail_id']
    genre = data['genre']
    return render_template("profile.html" ,name = user_name,Gmail = gmail,Genre = genre)