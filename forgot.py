from flask import Flask,redirect,render_template,request,url_for,session,jsonify
from db import db
import bcrypt
import random
from flask_mail import Mail, Message
from config import app,mail

def send_message():
    if request.method == 'POST':
        otp = str(random.randrange(10000, 99999))
        session['otp'] = str(otp)
        name = request.form['name']
        data = db.user_data.find_one({"$or":[{"name":name},{"mail_id":name}]})
        if data:
            email = data['mail_id']
            sub = "OTP verification"
            message = Message(sub,sender='ar8152270@gmail.com',recipients=[email])
            message.body = "YOUR OTP IS " + str(otp)
            mail.send(message)
            return redirect(url_for('verify'))
        return jsonify({"status":"please enter valid user name or mail Id !"})
    return render_template("email.html")

def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if session['otp'] == str(user_otp):
            return redirect(url_for('update_password'))
        else:
            return "invalid otp please try again"
    return render_template("verify.html")


def for_password():
    if request.method == 'POST':
        name = request.form['name']
        input_mail = request.form['mail']
        password1 = request.form['password']
        password2 = request.form['new_password']
        existing_user = db.user_data.find_one({"$and":[{"name":name},{"mail_id":input_mail}]})
        if existing_user:
            if password1 == password2:
                hashpass = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
                db.user_data.update_one({"name": name}, {"$set": {"password": hashpass}})
                return jsonify({"status":"password changed successfully !"})

        return jsonify({"status":"password or mail id missmatch !"})
    return render_template('forgot_password.html')