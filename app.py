from flask import Flask, render_template, request, jsonify

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
    new_id = len(contacts) + 1
    contacts.append({"id": new_id, "name": name, "email": email, "phone": phone})
    return render_template("index.html", contacts=contacts)

# REST API Routes

@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    return jsonify(contacts)

@app.route("/api/contacts/<int:contact_id>", methods=["GET"])
def get_contact(contact_id):
    contact = next((c for c in contacts if c["id"] == contact_id), None)
    if contact:
        return jsonify(contact)
    else:
        return jsonify({"message": "Contact not found"}), 404

@app.route("/api/contacts", methods=["POST"])
def create_contact():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data or "phone" not in data:
        return jsonify({"message": "Invalid data"}), 400
    new_id = len(contacts) + 1
    new_contact = {
        "id": new_id,
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
    }
    contacts.append(new_contact)
    return jsonify(new_contact), 201

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    contact = next((c for c in contacts if c["id"] == contact_id), None)
    if not contact:
        return jsonify({"message": "Contact not found"}), 404
    data = request.get_json()
    if not data or "name" not in data or "email" not in data or "phone" not in data:
        return jsonify({"message": "Invalid data"}), 400

    contact["name"] = data["name"]
    contact["email"] = data["email"]
    contact["phone"] = data["phone"]
    return jsonify(contact)

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    global contacts
    contacts = [c for c in contacts if c["id"] != contact_id]
    return jsonify({"message": "Contact deleted"})

if __name__ == "__main__":
    app.run(debug=True)