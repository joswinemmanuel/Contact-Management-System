from flask import Flask, redirect, render_template, request, jsonify
from model import db, Contact, init_db

app = Flask(__name__)

init_db(app)

# MVC Routes

@app.route("/")
def index():
    with app.app_context():
        contacts = db.session.execute(db.select(Contact)).scalars().all()
    return render_template("index.html", contacts=contacts)

@app.route("/new-contact")
def new_contact():
    return render_template("add-contact.html")

@app.route("/add", methods=["POST"])
def add_contact():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    new_contact = Contact(name=name, email=email, phone=phone)
    with app.app_context():
        db.session.add(new_contact)
        db.session.commit()
    return redirect("/")

@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact_mvc(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact:
            db.session.delete(contact)
            db.session.commit()
        return redirect("/")

# REST API Routes

@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    with app.app_context():
        contacts = db.session.execute(db.select(Contact)).scalars().all()
        if contacts:
            return jsonify([{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone} for c in contacts])
        else:
            return jsonify({"message": "No contacts available"}), 404

@app.route("/api/contacts/<int:contact_id>", methods=["GET"])
def get_contact(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact:
            return jsonify({"id": contact.id, "name": contact.name, "email": contact.email, "phone": contact.phone})
        else:
            return jsonify({"message": "Contact not found"}), 404

@app.route("/api/contacts", methods=["POST"])
def create_contact():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data or "phone" not in data:
        return jsonify({"message": "Invalid data"}), 400
    new_contact = Contact(name=data["name"], email=data["email"], phone=data["phone"])
    with app.app_context():
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"id": new_contact.id, "name": new_contact.name, "email": new_contact.email, "phone": new_contact.phone}), 201

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if not contact:
            return jsonify({"message": "Contact not found"}), 404
        data = request.get_json()
        if not data or "name" not in data or "email" not in data or "phone" not in data:
            return jsonify({"message": "Invalid data"}), 400

        contact.name = data["name"]
        contact.email = data["email"]
        contact.phone = data["phone"]
        db.session.commit()
        return jsonify({"id": contact.id, "name": contact.name, "email": contact.email, "phone": contact.phone})

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact:
            db.session.delete(contact)
            db.session.commit()
            return jsonify({"message": "Contact deleted"})
        else:
            return jsonify({"message": "Contact not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)