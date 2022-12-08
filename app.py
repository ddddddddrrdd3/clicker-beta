from flask import Flask, jsonify, redirect, render_template, request, url_for, session, make_response
from flask_socketio import SocketIO, emit
from mongo import *
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex()
app.jinja_env.globals.update(enumerate=enumerate)

socket = SocketIO(app)

@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        form = request.form

        username = form["username"]
        password = form["password"]

        user = find(username=username, password=password)

        if user:
            return render_template("skeletal.html", username=username)
        else:
            return render_template("login.html")

    return render_template("skeletal.html", username="")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html", top=get_top())

@app.route("/signup_validator", methods=["POST"])
def signup_validator():
    form = request.form
    username = form["username"]
    password = form["password"]
    if len(username) < 3:
        return "Username too short"
    invalid_username = ["fuck","ass","dick","retard","shit","nigga","nigger","puss","bitch",
                        "nazi","gay","lesbian","transgender","queer","sex","jayyong","piss","tit"
                        "cum","cock","thot","penis","vagina","boob","slut","twat","cunt","bastard","bollocks","testis","foreskin","anal","incest",
                        "geonocide","suicide","racist","sexist", #violence
                        "risingsunflag","japanwarflag","axispower","hirohito","hidekitojo""hitler","japanesewarflag"] #ww2

    invalid_username_num = []

    allowed_letters = ["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ1234567890_. "]
    unban_word = ["documantary","document","documentation",
                  "cockadoodledoo","cockadoodledo","cockadodledoo","cockadodledo","cockadoddledoo","cockadoddledo"]
    ini_string = username
 
    k = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVwXYZ";
    charlst = list(k)
 
    getVals = list(filter(lambda x: x in k, ini_string))
    result = "".join(getVals)
    valid = True
    for letters in username:
        if letters not in charlst:
            valid = False
            break
    for chars in username:
        if chars in invalid_username_num:
            valid = False
            break
    for bad_word in invalid_username:
        if bad_word in result:
            valid = False
            break
    for good_word in unban_word:
        if good_word in result:
            valid = True
            break
    if valid:
        create_user(username, password)
        return render_template("skeletal.html")
    else:
        #TODO window.aler("Your username is inapproriate")
        return "Inappropriate username"

@app.route('/username_and_pass_api')
def rickroll():
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


# Sockets

@socket.on("add")
def add(user, amount):
    # TODO: check apple amount
    add_apple(user, amount)

@socket.on("init")
def init(user):
    user_data = find(username=user)
    emit("apple", user_data["apple"])
    emit("inv", user_data["inventory"])
    emit("shop", SHOP)

@socket.on("buy")
def buy(user, item):
    print(user, item)
    user_data = find(username=user)
    price = SHOP[item] * 1.1 ** user_data["inventory"][item]
    apple = user_data["apple"]

    if apple >= price:
        add_apple(user, -price)
        add_item(user, item, 1)

        user_data["apple"] -= price
        user_data["inventory"][item] += 1

        emit("apple", user_data["apple"])
        emit("item", (item, user_data["inventory"][item]))
        emit("shop", SHOP)

    else:
        # TODO: handle not enough apple
        pass
        



if __name__ == "__main__":
    socket.run(app, debug=True)