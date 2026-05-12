from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
from datetime import datetime

from werkzeug.security import check_password_hash

from db import init_db, increment_counter, get_counter, get_user_by_username, create_user

app = Flask(__name__)
app.secret_key = "super-secret-key-change-in-production"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

init_db()


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_username("placeholder")  # placeholder to get connection working
    # We need to fetch the actual user by ID
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return User(row[0], row[1])
    return None


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
@login_required
def index():
    count = get_counter()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", count=count, current_time=current_time)


@app.route("/click", methods=["POST"])
@login_required
def click():
    count = increment_counter()
    message = random.choice(messages)
    return jsonify({
        "count": count,
        "message": message
    })


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user_data = get_user_by_username(username)
        if user_data and check_password_hash(user_data["password_hash"], password):
            user = User(user_data["id"], user_data["username"])
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Неверное имя пользователя или пароль", "error")
    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            flash("Имя пользователя и пароль обязательны", "error")
            return render_template("register.html")
        
        user = create_user(username, password)
        if user:
            flash("Регистрация успешна! Теперь войдите.", "success")
            return redirect(url_for("login"))
        else:
            flash("Пользователь с таким именем уже существует", "error")
    
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)