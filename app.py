from flask import Flask, request, render_template, redirect, url_for, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = '9df31cad3eb2f66386575da6dd664d4s'  # Change this to a secure key

# In-memory storage for users and secrets
users = {}
secrets = {}


# Route for registration
# Route for registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        if username in users:
            return "Username already exists. Try another."

        hashed_password = generate_password_hash(password)
        users[username] = hashed_password
        return redirect(url_for("login"))

    return render_template("register.html")


# Route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        stored_password = users.get(username)

        if stored_password and check_password_hash(stored_password, password):
            session["username"] = username
            return redirect(url_for("index"))
        return "Invalid credentials. Please try again."
    return render_template("login.html")


# Route for logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# Home page route
@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

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
    if "username" not in session:
        return redirect(url_for("login"))

    secret_message = secrets.pop(secret_id, None)
    if secret_message is None:
        abort(404)  # Secret not found or already viewed
    return render_template("secret.html", secret=secret_message)


if __name__ == "__main__":
    app.run(debug=True)
