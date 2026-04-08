from flask import Flask, render_template, jsonify
import random
from db import init_db, increment_counter, get_counter

app = Flask(__name__)
init_db()

messages = [
    "Вы восхитительны!",
    "Попробуй еще раз.",
    "А вот это уже слишком.",
    "Неплохо!",
    "Ты можешь лучше!",
    "Это было мощно!",
    "Хмм... странно.",
    "Продолжай!",
    "Ты серьезно?",
    "Легенда!"
]

@app.route("/")
def index():
    count = get_counter()
    return render_template("index.html", count = count)

@app.route("/click", methods=["POST"])
def click():
    count = increment_counter()
    message = random.choice(messages)
    return jsonify({
        "count": count,
        "message": message
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)