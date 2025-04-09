from flask import Flask, render_template, request

app = Flask(__name__)

# Storing data internally in a list rather than a database to test our Routes
contacts = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "phone": "123-456-7890"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "phone": "987-654-3210"},
]

# MVC Routes

@app.route("/")
def index():
    return render_template("index.html", contacts=contacts)

@app.route("/add", methods=["POST"])
def add_contact():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    new_id = len(contacts) + 1  # In a real app, use a database's auto-increment
    contacts.append({"id": new_id, "name": name, "email": email, "phone": phone})
    return render_template("index.html", contacts=contacts)

if __name__ == "__main__":
    app.run(debug=True)