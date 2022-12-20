from flask import Flask, render_template, url_for, request, session, redirect,jsonify
from db import db
import bcrypt

def new_register():
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        password = request.form['password']
        set_genre = request.form['gener']
        existing_user = db.user_data.find_one({'name': name})
        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            db.user_data.insert_one({'name': name, "mail_id":mail,"genre":set_genre, 'password': hashpass})
            return jsonify({"status":"Registration completed go to login now"})
        return jsonify({"status":'This username is already exists!'})
    return render_template('register.html')
