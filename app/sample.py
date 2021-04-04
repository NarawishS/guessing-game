from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os, json, redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient(
    'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ[
        'MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

myCollection = db.game


@application.route('/', methods=['post', 'get'])
def index():
    myCollection.delete_many({})
    return render_template("index.html")


@application.route('/game/start', methods=['post'])
def initialize():
    data = request.form['word']
    answer = []
    answer[:0] = data
    hint = []
    choice = []
    for i in range(0, len(answer)):
        hint.append("*")
        if answer[i] not in choice:
            choice.append(answer[i])
    myCollection.insert_one({
        "count": 0,
        "answer": answer,
        "choice": choice,
        "hint": hint,
        "guess": [],
        "end": False
    })
    return render_template('start.html')


@application.route('/game', methods=['post', 'get'])
def play():
    game = myCollection.find_one()
    if request.method == 'POST' and len(game['answer']) != len(game['guess']):
        data = request.form['choice']
        my_query = {"answer": game['answer']}
        answer = game['guess']
        answer.append(data)
        new_data = {"$set": {"guess": answer}}
        myCollection.update_one(my_query, new_data)
        if answer == game['answer']:
            myCollection.update_one(my_query, {"$set": {"end": True}})
    if len(game['answer']) == len(game['guess']) and game['answer'] != game['guess']:
        my_query = {"answer": game['answer']}
        count = game['count']
        count += 1
        myCollection.update_one(my_query, {"$set": {"count": count, "guess": []}})
    game = myCollection.find_one()
    return render_template("game.html", game=game)


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
