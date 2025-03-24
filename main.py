#pip install flask, tinydb, requests, bcrypt
from flask import Flask, render_template, request, jsonify, make_response
from tinydb import TinyDB, Query
import requests
import bcrypt
import base64
import uuid


app = Flask(__name__)

db = TinyDB('db.json')
User = Query()

class UserStateManager:
    def __init__(self):
        self.users = {}

    def login_user(self, user):
        id = str(uuid.uuid4())
        while id in self.users.values():
            id = str(uuid.uuid4())
        self.users[user] = id
    
    def logout_user(self, user):
        if user in self.users: self.users.pop(user)

usm = UserStateManager()


@app.route('/')
def signup():
    return render_template('signup.html')

@app.route('/registerUser', methods=["POST"])
def registerUser():
    username = request.json["username"]
    password = request.json["password"]

    if username == "" or password == "":
        return jsonify({"status": "empty input"})
    if len(db.search(User.username == username)) > 0:
        return jsonify({"status": "account already exists"})
    

    db.insert({"username": username, "password": hashText(password)})

    return jsonify({"status": "ok"})

@app.route('/loginUser', methods=["POST"])
def loginUser():
    username = request.json["username"]
    password = request.json["password"]

    users = db.search(User.username == username)
    if(len(users) > 0):
        user = users[0]
    else:
        return jsonify({"status": "invalid credentials"})

    if checkHash(user["password"], password):
        usm.login_user(username)
        
        response = make_response(jsonify({"status": "ok"}))
        response.set_cookie(
        "session_id", usm.users[username], 
            httponly=True,
            secure=True,  # samo https
            samesite="Strict",
            max_age=3600 #expire in [sec]
        )
        return response
    else:
        return jsonify({"status": "invalid credentials"})

@app.route("/checkSession", methods=["POST"])
def checkSession():
    session_id = request.cookies.get("session_id")
    if session_id in usm.users.values():
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "not found"})

@app.route("/logout", methods=["POST"])
def logout():
    session_id = request.cookies.get("session_id")
    user = list(usm.users.keys())[list(usm.users.values()).index(session_id)]
    usm.logout_user(user)

    response = make_response(jsonify({"status": "ok"}))
    response.delete_cookie("session_id")
    return response


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/workoutManager")
def workoutManager():
    return render_template("workoutManager.html")

@app.route("/workoutPlan")
def workoutPlan():
    return render_template("workoutPlan.html")


def hashText(text):
    hashed_bytes = bcrypt.hashpw(text.encode('utf-8'), bcrypt.gensalt())
    return base64.b64encode(hashed_bytes).decode('utf-8')

def checkHash(hashed_str, normal):
    hashed_bytes = base64.b64decode(hashed_str)
    return bcrypt.checkpw(normal.encode('utf-8'), hashed_bytes)





if __name__ == '__main__':
    app.run(debug=True)


