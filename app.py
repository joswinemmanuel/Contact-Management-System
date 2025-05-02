from flask import Flask, redirect, render_template, request, url_for, jsonify, session, send_from_directory, flash
import os
from model import db, Contact, init_db, User
from functools import wraps
from sqlalchemy import or_
from sqlalchemy.orm import Query
from datetime import datetime
from werkzeug.utils import secure_filename
from random import choice, randint
from faker import Faker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
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
    error = None
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
            
        if not username:
            error = 'Username must not be empty'
        elif not first_name:
            error = 'First name must not be empty'
        elif not last_name:
            error = 'Last name must not be empty'
        elif not email:
            error = 'Email address must not be empty'
        elif '@' not in email or '.' not in email:
            error = 'Invalid email format'
        elif not password:
            error = 'Password must not be empty'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters long'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif not date_of_birth:
            error = 'Date must not be empty'
        elif not gender:
            error = 'Gender must not be empty'
        elif not phone_number:
            error = 'Phone number must not be empty'
        elif not address:
            error = 'Address must not be empty'
        elif not profile_picture:
            error = 'Profile picture must be uploaded'
        
        if not error:
            with app.app_context():
                if User.query.filter_by(username=username).first():
                    return render_template('register.html', error_msg='Username already exists')
                if User.query.filter_by(email=email).first():
                    return render_template('register.html', error_msg='Email address already exists')

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
                flash(f"Welcome { session['first_name'] }, You have successfully registered", "primary")
                return redirect(url_for('login'))
        else:
            return render_template('register.html', error=error)
    return render_template('register.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    fake = Faker()
    with app.app_context():
        first_name=fake.first_name()
        db.session.add(Contact(
                first_name=first_name,
                last_name=fake.last_name(),
                address=fake.city(),
                company=choice(["Innovature", "TechNova", "SoftLoop", "CodeWave"]),
                email=first_name.lower()+"@gmail.com",
                phone_number=str(randint(9000000000, 9999999999)),
                created_by_user_id=session["user_id"]
            ))
        db.session.commit()
    return render_template('test.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            error = "Username must not be empty"
        elif not password:
            error = "Password must not be empty"

        if not error:
            with app.app_context():
                user = User.query.filter_by(username=username).first()
                if user and user.check_password(password):
                    session['user_id'] = user.id
                    session['first_name'] = user.first_name
                    session['last_name'] = user.last_name
                    flash(f"Welcome { session['first_name'] }, You have successfully logged in", "primary")
                    return redirect(url_for('contacts'))
                elif user:
                    flash("Password is incorrect", "danger")
                    return render_template('login.html', error='Invalid password')
                else:
                    flash(f"Username doesn't exist", "danger")
                    return render_template('login.html', error='Invalid username')
        else:
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash(f"Goodbye { session['first_name'] }, You have been logged out safely", "primary")
    return redirect(url_for('login'))

@app.route("/contacts", defaults={'page': 1})
@app.route("/contacts/page/<int:page>")
@login_required
def contacts(page):
    contacts_per_page = 5
    user_id = session['user_id']

    with app.app_context():
        query: Query = db.session.query(Contact).filter_by(created_by_user_id=user_id).order_by(Contact.first_name, Contact.last_name)
        total_contacts = query.count()
        contacts = query.paginate(page=page, per_page=contacts_per_page, error_out=False)

        return render_template("contacts.html", contacts=contacts, total_contacts=total_contacts, contacts_per_page=contacts_per_page)


@app.route("/profile")
@login_required
def profile():
    user_id = session['user_id']
    with app.app_context():
        user = db.session.get(User, user_id)
        if user:
            return render_template('profile.html', user=user)
        else:
            flash('User profile not found.', 'danger')
            return redirect(url_for('contacts'))
        
@app.route('/edit-profile', methods=['GET'])
@login_required
def edit_profile():
    user_id = session['user_id']
    with app.app_context():
        user = db.session.get(User, user_id)
        if user:
            return render_template('edit-profile.html', user=user)
        else:
            flash('User profile not found.', 'danger')
            return redirect(url_for('profile'))

@app.route('/edit-profile', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user_id']
    with app.app_context():
        user = db.session.get(User, user_id)
        error = None

        username = request.form['username']
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form['email']
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone_number = request.form['phone_number']
        address = request.form.get('address')
        profile_picture = request.files.get('profile_picture')

        if not username:
            error = 'Username must not be empty'
        elif not first_name:
            error = 'First name must not be empty'
        elif not last_name:
            error = 'Last name must not be empty'
        elif not email:
            error = 'Email address must not be empty'
        elif '@' not in email or '.' not in email:
            error = 'Invalid email format'
        elif not date_of_birth:
            error = 'Date must not be empty'
        elif not gender:
            error = 'Gender must not be empty'
        elif not phone_number:
            error = 'Phone number must not be empty'
        elif not address:
            error = 'Address must not be empty'

        if not error:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date() if date_of_birth else None
            user.gender = gender
            user.phone_number = phone_number
            user.address = address
            if profile_picture and allowed_file(profile_picture.filename):
                    filename = secure_filename(profile_picture.filename)
                    profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user.profile_picture = filename
            db.session.commit()
            flash('Profile Updated', 'info')
            return redirect(url_for('profile'))
        else:
            return render_template("edit-profile.html", error=error, user=user)

@app.route("/search", methods=["GET"], defaults={'page': 1})
@app.route("/search/page/<int:page>", methods=["GET"])
@login_required
def search_contacts(page):
    query = request.args.get("query")
    contacts_per_page = 5
    user_id = session['user_id']

    if query:
        search_term = f"%{query}%"
        if len(search_term) == 3:
            search_term = search_term[1:]

        with app.app_context():
            search_query: Query = db.session.query(Contact).filter(
                Contact.created_by_user_id == user_id,
                or_(
                    Contact.first_name.like(search_term),
                    Contact.email.like(search_term),
                    Contact.phone_number.like(search_term)
                )
            ).order_by(Contact.first_name, Contact.last_name)

            total_results = search_query.count()
            results_pagination = search_query.paginate(page=page, per_page=contacts_per_page, error_out=False)

            if request.args.get("new-search"):
                flash("Search Results", "info")

            return render_template("contacts.html", contacts=results_pagination, total_contacts=total_results, contacts_per_page=contacts_per_page, search_query=query)
    else:
        flash("All Contacts", "info")
        return redirect(url_for('contacts'))


@app.route("/new-contact")
@login_required
def new_contact():
    return render_template("add-contact.html")

@app.route("/add", methods=["POST"])
@login_required
def add_contact():
    error = None

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    address = request.form.get('address')
    company = request.form.get('company')
    email = request.form['email']
    phone_number = request.form['phone_number']
    created_by_user_id = session['user_id']

    if not first_name:
        error = 'First name must not be empty'
    elif not last_name:
        error = 'Last name must not be empty'
    elif not address:
        error = 'Address must not be empty'
    elif not company:
        error = 'Company must not be empty'
    elif not email:
        error = 'Email must not be empty'
    elif '@' not in email or '.' not in email:
        error = 'Invalid email format'
    elif not phone_number:
        error = 'Phone number must not be empty'
    if not error:
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
    else:
        return render_template("add-contact.html", error=error)

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
        error = None

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        company = request.form.get('company')
        email = request.form['email']
        phone_number = request.form['phone_number']

        if not first_name:
            error = 'First name must not be empty'
        elif not last_name:
            error = 'Last name must not be empty'
        elif not address:
            error = 'Address must not be empty'
        elif not company:
            error = 'Company must not be empty'
        elif not email:
            error = 'Email must not be empty'
        elif '@' not in email or '.' not in email:
            error = 'Invalid email format'
        elif not phone_number:
            error = 'Phone number must not be empty'
        
        if not error: 
            if contact and contact.created_by_user_id == session['user_id']:
                contact.first_name = first_name
                contact.last_name = last_name
                contact.address = address
                contact.company = company
                contact.email = email
                contact.phone_number = phone_number
                db.session.commit()
                flash(f"Contact Edited", "info")
                return redirect(url_for('contacts'))
            else:
                flash("Contact not found")
                return redirect(url_for('contacts'))
        else:
            return render_template("edit-contact.html", error=error, contact=contact)


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