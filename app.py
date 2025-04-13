from flask import Flask, redirect, render_template, request, url_for, jsonify, session, send_from_directory
import os
from model import db, Contact, init_db, User
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
init_db(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'CMS.ico', mimetype='image/vnd.microsoft.icon')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        with app.app_context():
            if User.query.filter_by(username=username).first():
                return render_template('register.html', error='Username already exists')

            new_user = User(username=username, email=email, phone=phone)
            new_user.set_password(password)
            new_contact = Contact(name=username, email=email, phone=phone)
            db.session.add(new_user)
            db.session.add(new_contact)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                return redirect(url_for('contacts'))
            else:
                return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('landing'))

# MVC Routes

@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('contacts'))
    return render_template('landing.html')

@app.route("/contacts")
@login_required
def contacts():
    with app.app_context():
        contacts = db.session.execute(db.select(Contact)).scalars().all()
    return render_template("contacts.html", contacts=contacts)

@app.route("/new-contact")
@login_required
def new_contact():
    return render_template("add-contact.html")

@app.route("/add", methods=["POST"])
@login_required
def add_contact():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    new_contact = Contact(name=name, email=email, phone=phone)
    with app.app_context():
        db.session.add(new_contact)
        db.session.commit()
    return redirect("/contacts")

@app.route("/delete/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact_mvc(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact:
            db.session.delete(contact)
            db.session.commit()
        return redirect("/contacts")

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