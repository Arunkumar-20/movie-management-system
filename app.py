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
                #return jsonify({"status":"login successfull"})
                return redirect(url_for("dashboard"))
        return jsonify({"status":'Invalid username/password combination'})

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
        movie = db.movies.find()
        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': name, 'password': hashpass})
            for movies in movie:
                m_name = (movies["movie_name"])
                db.user_data.update_one({"name": name}, {"$set": {m_name: 0}})
            return jsonify({"status":"Registration completed go to login now"})

        return jsonify({"status":'This username is already exists!'})
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
        data = db.movies
        user = db.user_data
        existing_movie = data.find_one({"movie_name":movie_name})

        if existing_movie is None:
            data.insert_one({"movie_name": movie_name, "relese_date": date, "movie_type": type, "upvote":0, "downvote":0})
            user.update_many({ },{"$set":{movie_name:0}})
            #db.vote.insert_one({"username":session["name"],"movie_name":movie_name,"up":True,"down":True})
            return jsonify({"status":"movie insertes sucessfully"})
           # return redirect(url_for('viewmovie'))
        else:
            return jsonify({"status":"This movie is allready exists"})
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
            return jsonify({"status": "movie updated sucessfully"})
            #return redirect(url_for("viewmovie"))
    return render_template("editmovie.html")

@app.route('/deletemovie', methods=['GET','POST'])
@login_required
def deletemovie():
    if request.method == 'POST':
        name = request.form['name']
        data = db.movies
        existing_movie = data.find_one({"movie_name":name})

        if existing_movie:
            data.delete_one({"movie_name":name})
            return jsonify({"status": "movie deleted sucessfully"})
        else:
            return jsonify({"status":"Enter valid movie name"})
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
                return jsonify({"status":"comments added successfully"})
                #return redirect(url_for("viewmovie"))
            else:
                return  jsonify({"status":"This movie is not DB"})
        return render_template("comments.html")

@app.route('/vote',methods=["POST","GET"])
@login_required
def voteing():
    if request.method == 'POST':
        movie = request.form['name']
        vote_type = request.form['vote']
        user = session['name']
        data = db.movies
        movies = data.find_one({"movie_name": movie})
        if movies:
            upvote = movies['upvote']
            downvote = movies['downvote']
        else:
            return jsonify({"status":"please enter the valid movie !"})
        user_name = db.user_data.find_one({"name": user})
        if movies:
            if vote_type == "upvote":
                if user_name[movie] == 0:
                    up_vote = upvote + 1
                    db.movies.update_one({"movie_name": movie}, {"$set": {"upvote": up_vote}})
                    db.user_data.update_one({"name": user}, {"$set": {movie: 1}})
                    return jsonify({"status":"upvote added successfully"})

            if vote_type == "downvote":
                if user_name[movie] == 0:
                    down_vote = downvote + 1
                    db.movies.update_one({"movie_name": movie}, {"$set": {"downvote": down_vote}})
                    db.user_data.update_one({"name": user}, {"$set": {movie: 2}})
                    return jsonify({"status":"downvote added successfully"})

            if vote_type == "downvote":
                if user_name[movie] == 1:
                    up_vote = upvote - 1
                    down_vote = downvote + 1
                    db.movies.update_one({"movie_name": movie}, {"$set": {"downvote": down_vote}})
                    db.movies.update_one({"movie_name": movie}, {"$set": {"upvote": up_vote}})
                    db.user_data.update_one({"name": user}, {"$set": {movie: 2}})
                    return jsonify({"status":"downvote added successfully"})

            if vote_type == "upvote":
                if user_name[movie] == 2:
                    up_vote = upvote + 1
                    down_vote = downvote - 1
                    db.movies.update_many({"movie_name": movie}, {"$set": {"downvote": down_vote, "upvote": up_vote}})
                    db.user_data.update_one({"name": user}, {"$set": {movie: 1}})
                    return jsonify({"status":"upvote added successfully"})

        return jsonify({"status":"please enter correct movie name !"})

    return render_template("vote.html")

@app.route('/search',methods=['POST','GET'])
@login_required  # filter by votes using counts of upvote and downvote
def search():
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

@app.route('/recommendation',methods=['POST','GET'])
@login_required
def recommendation():
    if request.method == 'POST':
        type = request.form['gener']
        data = db.movies.find({"movie_type":type})
        return render_template("movies.html",data=data)
    return render_template("recommendation.html")

if __name__ == '__main__':
    app.run(debug=True,port=7000)
