from flask import Flask, render_template, url_for, request, session, redirect,jsonify
import pymongo
import bcrypt
from functools import wraps
from flask_login import UserMixin,login_user,LoginManager,login_required,current_user,logout_user
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'mysecret'
client = pymongo.MongoClient("mongodb+srv://m001-student:arun-2002@cluster0.trsumto.mongodb.net/?retryWrites=true&w=majority")
db = client.login_users

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(name):
    users = db.user_data
    data = users.find_one({'name':name})
    if data:
        return User(name=data['name'],password=data['password'])
    else:
        return None

class User(UserMixin):
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
        return 'Invalid username/password combination'
    return render_template("login.html")

@app.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        users = db.user_data
        existing_user = users.find_one({'name': name})

        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': name, 'password': hashpass})
            session['name'] = name
            return redirect(url_for('index'))
        return 'That username already exists!'
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('name',None)
    return redirect(url_for("login"))

@app.route('/addmovie', methods=['POST','GET'])
@login_required
def addmovie():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        date = request.form['date']
        type = request.form['type']
        up_vote = int(request.form['upvote'])
        down_vote = int(request.form['downvote'])
        data = db.movies
        existing_movie = data.find_one({"movie_name":movie_name})

        if existing_movie is None:
            data.insert_one({"movie_name": movie_name, "relese_date": date, "movie_type": type, "upvote":up_vote, "downvote":down_vote})
            return redirect(url_for('viewmovie'))
        else:
            return "this movie allready exists"
    return render_template("addmovie.html")

@app.route('/editmovie', methods=['POST','GET'])
@login_required
def editmovie():
    if request.method == 'POST':
        name = request.form['movie_name']
        date = request.form['date']
        type = request.form['type']
        data = db.movies
        existing_movie = data.find_one({"movie_name":name})

        if existing_movie:
            data.update_one({"movie_name":name},{"$set":{"movie_name":name,"relese_date":date,"movie_type":type}})
            return redirect(url_for("viewmovie"))
    return render_template("editmovie.html")

@app.route('/deletemovie', methods=['POST','GET'])
@login_required
def deletemovie():
    if request.method == 'POST':
        name = request.form['name']
        data = db.movies
        existing_movie = data.find_one({"movie_name":name})

        if existing_movie:
            data.delete_one({"movie_name":name})
            return redirect(url_for("viewmovie"))
        else:
            return "Enter valid movie name"
    return render_template("deletemovie.html")


@app.route('/viewmovie',methods=['POST','GET'])
@login_required
def viewmovie():
    if request.method == 'GET':
        data = db.movies.find()
        return render_template("viewmovie.html",data=data)

@app.route('/find',methods=['POST','GET'])
@login_required
def find():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['r_date']
        data = db.movies.find_one({"$or":[{"movie_name":name},{"relese_date":date}]})
        movie_name = data["movie_name"]
        movie_type = data["movie_type"]
        relese_date = data["relese_date"]
        up_vote = data["upvote"]
        down_vote = data["downvote"]
        if data:
            return render_template("detial.html",name=movie_name,type=movie_type,date=relese_date,upvote=up_vote,downvote=down_vote)
        else:
            return "invalid movie name"
    return render_template("find.html")
    # except:
    #     return "enter valid movie"

@app.route("/comments",methods=['POST','GET'])
@login_required
def comments():
        if request.method == 'POST':
            name = request.form['name']
            comment = request.form['comments']
            data = db.movies
            existing_movie = data.find_one({"movie_name": name})

            if existing_movie:
                data.update_one({"movie_name": name}, {"$push": {"comments":[session['name'],comment]}})
                return redirect(url_for("viewmovie"))
            else:
                "This movie is not DB"
        return render_template("comments.html")

@app.route('/vote',methods=["POST","GET"])
def voteing():
    if request.method == 'POST':
        name = request.form['name']
        vote = request.form['vote']
        data = db.movies
        movie = data.find_one({"movie_name": name})
        up_vote = movie['upvote']
        down_vote = movie['downvote']
        if movie:
            if vote == 'upvote':
                upvote = up_vote + 1
                data.update_one({"movie_name": name}, {"$set": {"upvote": upvote}})
                return "upvote added successfully"

            if vote == 'downvote':
                downvote = down_vote + 1
                data.update_one({"movie_name": name}, {"$set": {"downvote": downvote}})
                return "downvote added successfully"

        return " this movie is not exist !"

    return render_template("vote.html")


if __name__ == '__main__':
    app.run(debug=True,port=8000)



