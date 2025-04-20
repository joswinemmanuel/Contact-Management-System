from flask import Flask, redirect, render_template, request, url_for, jsonify, session, send_from_directory, flash
import os
from model import db, Contact, init_db, User
from functools import wraps
from sqlalchemy import or_
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
init_db(app)
app.config['UPLOAD_FOLDER'] = 'static/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# MVC Routes

@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('contacts'))
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone_number = request.form['phone_number']
        address = request.form.get('address')
        profile_picture = request.files.get('profile_picture')
            
        with app.app_context():
            if User.query.filter_by(username=username).first():
                return render_template('register.html', error='Username already exists')
            if User.query.filter_by(email=email).first():
                return render_template('register.html', error='Email address already exists')
            if password != confirm_password:
                return render_template('register.html', error='Passwords do not match')

            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                date_of_birth=datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None,
                gender=gender,
                phone_number=phone_number,
                address=address
            )
            new_user.set_password(password)
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_user.profile_picture = filename
            db.session.add(new_user)
            db.session.commit()
            flash(f"Welcome { session['first_name'] }! You have successfully registered", "primary")
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        profile_picture = request.files.get('profile_picture')               
        print(profile_picture)
        if profile_picture and allowed_file(profile_picture.filename):
            print(allowed_file(profile_picture.filename))
            filename = secure_filename(profile_picture.filename)
            print(filename)            
        return redirect(url_for('test'))
    return render_template('test.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['first_name'] = user.first_name
                session['last_name'] = user.last_name
                flash(f"Welcome back, { session['first_name'] }! You have successfully logged in", "primary")
                return redirect(url_for('contacts'))
            elif user:
                flash("Password is incorrect", "danger")
                return render_template('login.html', error='Invalid password')
            else:
                flash(f"Username doesn't exist", "danger")
                return render_template('login.html', error='Invalid username')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash(f"Goodbye, { session['first_name'] }! You have been logged out safely", "primary")
    return redirect(url_for('login'))

@app.route("/contacts")
@login_required
def contacts():
    with app.app_context():
        contacts = db.session.execute(
            db.select(Contact)
            .filter_by(created_by_user_id=session['user_id'])
            .order_by(Contact.first_name, Contact.last_name)
        ).scalars().all()
    return render_template("contacts.html", contacts=contacts)

@app.route("/search", methods=["GET"])
@login_required
def search_contacts():
    query = request.args.get("query")
    if query:
        search_term = f"%{query}%"
        if len(search_term) == 3:
            search_term = search_term[1:]
        with app.app_context():
            results = db.session.execute(db.select(Contact).filter(
                Contact.created_by_user_id == session['user_id'],
                or_(
                    Contact.first_name.like(search_term),
                    Contact.email.like(search_term),
                    Contact.phone_number.like(search_term)
                )
            )).scalars().all()
        flash("Search results", "info")
        return render_template("contacts.html", contacts=results)
    else:
        flash("All contacts", "info")
        return redirect(url_for('contacts'))

@app.route("/new-contact")
@login_required
def new_contact():
    return render_template("add-contact.html")

@app.route("/add", methods=["POST"])
@login_required
def add_contact():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    company = request.form.get('company')
    email = request.form['email']
    phone_number = request.form['phone_number']
    created_by_user_id = session['user_id']
    new_contact = Contact(
        first_name=first_name,
        last_name=last_name,
        address=address,
        company=company,
        email=email,
        phone_number=phone_number,
        created_by_user_id=created_by_user_id
    )
    with app.app_context():
        db.session.add(new_contact)
        db.session.commit()
    flash("New contact added", "info")
    return redirect("/contacts")

@app.route("/edit/<int:contact_id>", methods=["GET"])
@login_required
def edit_contact(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact and contact.created_by_user_id == session['user_id']:
            return render_template("edit-contact.html", contact=contact)
        else:
            flash("Contact not found", "danger")
            return redirect(url_for('contacts'))
        
@app.route("/edit/<int:contact_id>", methods=["POST"])
@login_required
def update_contact(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact and contact.created_by_user_id == session['user_id']:
            contact.first_name = request.form.get("first_name")
            contact.last_name = request.form.get("last_name")
            contact.address = request.form.get("address")
            contact.company = request.form.get("company")
            contact.email = request.form.get("email")
            contact.phone_number = request.form.get("phone_number")
            db.session.commit()
            flash(f"Contact Edited", "info")
            return redirect(url_for('contacts'))
        else:
            flash("Contact not found")
            return redirect(url_for('contacts'))


@app.route("/delete/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact_mvc(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact and contact.created_by_user_id == session['user_id']:
            db.session.delete(contact)
            db.session.commit()
        flash("Contact Deleted")
        return redirect("/contacts")

# REST API Routes

@app.route("/api/contacts", methods=["GET"])
def get_contacts_api():
    with app.app_context():
        contacts = db.session.execute(db.select(Contact)).scalars().all()
        if contacts:
            return jsonify([{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone} for c in contacts])
        else:
            return jsonify({"message": "No contacts available"}), 404

@app.route("/api/contacts/<int:contact_id>", methods=["GET"])
def get_contact_api(contact_id):
    with app.app_context():
        contact = db.session.get(Contact, contact_id)
        if contact:
            return jsonify({"id": contact.id, "name": contact.name, "email": contact.email, "phone": contact.phone})
        else:
            return jsonify({"message": "Contact not found"}), 404

@app.route("/api/contacts", methods=["POST"])
def create_contact_api():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data or "phone" not in data:
        return jsonify({"message": "Invalid data"}), 400
    new_contact = Contact(name=data["name"], email=data["email"], phone=data["phone"])
    with app.app_context():
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"id": new_contact.id, "name": new_contact.name, "email": new_contact.email, "phone": new_contact.phone}), 201

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
def update_contact_api(contact_id):
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
def delete_contact_api(contact_id):
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