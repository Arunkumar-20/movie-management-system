from flask import Flask
from flask_mail import Mail, Message
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'mysecret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ar8152270@gmail.com'
app.config['MAIL_PASSWORD'] = 'uqbrfebydtnzxxwx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.secret_key='1234'

mail = Mail(app)