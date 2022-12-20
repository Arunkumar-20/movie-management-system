from flask import Flask, render_template, url_for, request, session, redirect,jsonify
import bcrypt
from flask_login import UserMixin,login_user,LoginManager,login_required,current_user,logout_user
from mail import send_message,verify_otp,update
from db import db
from config import app,login_manager
from profile import user_profile
from forgot import for_password,send_message,verify_otp
from update_genre import update_genre
from search_by_vote import search_by_vote
from votes import votes
from search import searching,user_recommended,add_comments
from movies import add_movie,edit_movie,delete_movie
from register import new_register


@login_manager.user_loader
def load_user(name):  # this funtion used to (reload the user object from the user name stored in session)
    data = db.user_data.find_one({'name':name})
    if data:
        return User(name=data['name'],password=data['password'])
    else:
        return None

class User(UserMixin):   #UserMixin is part of flask-login package that implements user authentication functionality.
    def __init__(self,name=None,password=None):
        self.name = name
        self.password = password


    def get_id(self):
        return self.name

@app.route('/',methods=['POST','GET'])
@login_required
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        users = db.user_data   # collection name = user_data
        name = request.form['name']
        password = request.form['password']
        Login_user = users.find_one({'name': name})
        if Login_user:
            if bcrypt.hashpw(password.encode('utf-8'), Login_user['password']) == Login_user['password']:
                logged_user = User(Login_user['name'], Login_user['password'])
                login_user(logged_user)
                session['name'] = Login_user['name']
                return redirect(url_for("dashboard"))
        return jsonify({"status":'Invalid username/password combination'})

    return render_template("login.html")

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    return new_register()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('name',None)
    return redirect(url_for("login"))

@app.route('/addmovie', methods=['POST','GET'])
@login_required
def addmovie():
    return add_movie()

@app.route('/editmovie/<movieid>', methods=['GET','POST'])
@login_required
def editmovie(movieid):
    return edit_movie(movieid)

@app.route('/deletemovie/<movieid>', methods=['GET','POST'])
@login_required
def deletemovie(movieid):
    return delete_movie(movieid)

@app.route('/viewmovie',methods=['POST','GET'])
@login_required
def viewmovie():
    if request.method == 'GET':
        data = db.movies.find()
        return render_template("movies.html",data=data)

@app.route('/recommendation',methods=['POST','GET'])
@login_required
def recommended():
    return user_recommended()

@app.route('/find',methods=['POST','GET'])
@login_required
def find():
    return searching()


@app.route("/comments/<movieid>",methods=['POST','GET'])
@login_required
def comments(movieid):
    return add_comments(movieid)

@app.route('/vote/<movieid>',methods=["POST","GET"])
@login_required
def voteing(movieid):
    return votes(movieid)

@app.route('/search',methods=['POST','GET'])
@login_required  # filter by votes using counts of upvote and downvote
def search():
    return search_by_vote()

@app.route('/genre',methods=['POST','GET'])
@login_required
def movie_type():
    return update_genre()

@app.route('/mail_send' ,methods=["POST","GET"])
def send_mail():
    return send_message()

@app.route('/verify_otp',methods=['GET','POST'])
def verify():
    return verify_otp()

@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    return send_message()

@app.route('/update_password', methods=['POST', 'GET'])
def update_password():
    return for_password()

@app.route('/profile')
@login_required
def profile():
    return user_profile()

@app.route('/update_data',methods=['GET','POST'])
@login_required
def update_data():
    return update()

if __name__ == '__main__':
    app.run(debug=True,port=8000)
