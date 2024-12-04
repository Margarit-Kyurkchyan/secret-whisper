from flask import Flask, request, redirect, render_template, url_for, abort
import uuid

app = Flask(__name__)

# In-memory storage for secrets
secrets = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the secret message from the form
        secret_message = request.form["secret"]
        # Generate a unique ID for the secret
        secret_id = str(uuid.uuid4())
        # Store the secret in the dictionary
        secrets[secret_id] = secret_message
        # Generate the secret link
        secret_link = url_for('reveal_secret', secret_id=secret_id, _external=True)
        return render_template("index.html", secret_link=secret_link)
    return render_template("index.html")

@app.route("/secret/<secret_id>")
def reveal_secret(secret_id):
    # Retrieve and remove the secret
    secret_message = secrets.pop(secret_id, None)
    if secret_message is None:
        abort(404)  # Secret not found or already viewed
    return render_template("secret.html", secret=secret_message)

if __name__ == "__main__":
    app.run(debug=True)
