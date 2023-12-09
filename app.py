from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin,current_user, login_user,logout_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from forms.authenticationForm import Registration, Login
from uuid import uuid4
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, send, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins = "*")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = str(uuid4())
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view ="login"
db = SQLAlchemy(app)

authUsername = None #This is for getting the signed in user's username
authId = None #userId
roomUserId = None #This is for getting the userId to be used as a roomId

class AuthUser():
    def __init__(self, username, id):
        '''
            this class serves as the class that will hold user value and carry it over to the template
        '''
        self.username = username
        self.id = id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

def authenticatin(newValueusername, newValueId):
    '''
        This function collects the authenticated users username and id by changing the globale variables authUsername and authId
        Arguments:
            newValueusername(string) : collects username
            newValueId(string) : collects id
    '''
    global authUsername
    global authId
    authUsername = newValueusername
    authId = newValueId

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
            authenticatin(user.username, user.id) #The global variables have been changed
            return redirect(url_for("Index"))
    return render_template("Registration.html", form = form)


@app.route("/login", methods=["POST","GET"])
def login():
    form = Login()
    userName = form.Username.data
    passWord = form.Password.data
    if request.method and form.validate_on_submit():
       user = db.session.query(User).filter_by(username = userName).first()
       authenticatin(user.username, user.id) #The global variables have been changed
       if user is not None:
           checkPassword = bcrypt.check_password_hash(user.password, passWord)
           if checkPassword:
               login_user(user)
               return redirect(url_for("Index"))
    return render_template("Login.html", form=form)


@app.route("/home")
def home():
    user = None
    if current_user.is_authenticated is False:
        return redirect(url_for("login"))
    authUser = AuthUser(authUsername,authId)
    return render_template("home.html", current_user=current_user, authUser = authUser)

@app.route('/', methods=["Get","POST"])
def Index():
    user = None
    if current_user.is_authenticated is False:
        return redirect(url_for("login"))
    authUser = AuthUser(authUsername, authId)
    users = db.session.query(User).all()
    return render_template("Index.html", users = users, userID = authUser.id)

@app.route('/landingPage/')
def LandingPage():
    return render_template("landingpage.html")

@app.route('/features')
def Features():
    return render_template("features.html")

@app.route('/about')
def About():
    return render_template("about.html")

#handles the private chat template
@app.route('/chat/<userId>', methods=['GET', 'POST'])
def privateChatPage(userId):
    global roomUserId
    roomUserId = userId
    roomusername = db.session.query(User).filter_by(id = roomUserId).first().username
    user = AuthUser(authUsername, authId)
    return render_template('chat.html', roomUserId = roomUserId, roomusername = roomusername, username = user.username)

@socketio.on('Generalmessage')
def handle_generalMessage(message):
    user = AuthUser(authUsername, authId)
    emit("GeneralMessageSendBack", { "message": message, "username": user.username }, broadcast = True)

@socketio.on('message')
def handle_messages(message):
    user = AuthUser(authUsername, authId)
    # allowed_users = [str(message["channelName"]), str(user.id)]
    # connected_clients = socketio.server.manager.get_participants(room=message["channelName"], namespace='/')
    # for client in connected_clients:
    #     client_user_id = socketio.server.manager.rooms[client][0]
    #     if client_user_id in allowed_users:
    emit("messageSendBack", {"message": message["message"], "username": user.username}, room=message["channelName"])
    #print("Message Received: " + message["message"])




# @socketio.on('Privatemessage')
# def privateChatEvent(Privatemessage):
#     userObj = User(authUsername,authId)
#     username = userObj.username
#     print(Privatemessage)
#     emit("privateMessageSendBack", {"message": Privatemessage, "username":username}, broadcast= True)

@socketio.on('joinRoom')
def joinRoom(data):
    print(data["username"] + 'Has joined ' + data["channelName"])
    join_room(data['channelName'])


if __name__ == "__main__":
    #app.run(debug=True)
    # socketio.run(app , host="localhost", debug = True)
    socketio.run(app , debug = True)