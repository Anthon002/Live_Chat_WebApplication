from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin,current_user, login_user,logout_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from forms.authenticationForm import Registration, Login
from uuid import uuid4
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = str(uuid4())
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view ="login"
db = SQLAlchemy(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["POST","GET"])
def registration():
    form = Registration()
    userName = form.Username.data
    passWord = form.Password.data
    if request.method == "POST" and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(passWord)
        newuser = User(username = userName, password = hashed_password)
        user = db.session.query(User).filter_by(username = userName).first()
        if user is not None:
            return None # to be change to flash error message
        else:
            db.session.add(newuser)
            db.session.commit()
    return render_template("Registration.html", form = form)


@app.route("/login", methods=["POST","GET"])
def login():
    form = Login()
    userName = form.Username.data
    passWord = form.Password.data
    if request.method and form.validate_on_submit():
       user = db.session.query(User).filter_by(username = userName).first()
       if user is not None:
           checkPassword = bcrypt.check_password_hash(user.password, passWord)
           if checkPassword:
               login_user(user)
               return redirect(url_for("home"))
    return render_template("Login.html", form=form)



@app.route("/home")
def home():
    if current_user.is_authenticated is False:
        return redirect(url_for("registration"))
    
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)