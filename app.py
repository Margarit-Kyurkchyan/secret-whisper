import uuid

from flask import Flask, request, render_template, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)


# Define routes (register, login, etc.)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Try another."

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session["username"] = username
            return redirect(url_for("index"))

        return "Invalid credentials. Please try again."

    return render_template("login.html")


# Route for logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# In-memory storage for secrets
secrets = {}


# Home page route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        secret_message = request.form["secret"]
        secret_id = str(uuid.uuid4())
        secrets[secret_id] = secret_message
        secret_link = url_for('reveal_secret', secret_id=secret_id, _external=True)
        return render_template("index.html", secret_link=secret_link)

    return render_template("index.html")


# Route to reveal the secret
@app.route("/secret/<secret_id>")
def reveal_secret(secret_id):
    secret_message = secrets.pop(secret_id, None)
    if secret_message is None:
        abort(404)  # Secret not found or already viewed
    return render_template("secret.html", secret=secret_message)


if __name__ == "__main__":
    app.run(debug=True)
