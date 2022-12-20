from flask import Flask,redirect,render_template,request,url_for,session,jsonify
from flask_mail import Mail, Message
import random
from config import mail
from db import db


def send_message():
    if request.method == 'POST':
        otp = str(random.randrange(10000, 99999))
        session['otp'] = str(otp)
        name = request.form['name']
        data = db.user_data.find_one({"name":name})
        if data:
            email = data['mail_id']
            sub = "OTP verification"
            message = Message(sub,sender='ar8152270@gmail.com',recipients=[email])
            message.body = "YOUR OTP IS " + str(otp)
            mail.send(message)
            return redirect(url_for('verify'))
        return jsonify({"status":"please enter valid user name !"})
    return render_template("email.html")

def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if session['otp'] == str(user_otp):
            return redirect(url_for('update_data'))
        else:
            return jsonify({"status":"invalid otp please try again"})
    return render_template("verify.html")

def update():
    if request.method == 'POST':
        name = request.form['name']
        movie_type = request.form['genre']
        mail = request.form['mail']
        db.user_data.update_one({"name":name},{"$set":{"genre":movie_type,"mail_id":mail}})
        return jsonify({"status":"data updated successfully !"})
    return render_template("update_profile.html")


