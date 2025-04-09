from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'
    
# SQLite Database
def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
    db.init_app(app)

    with app.app_context():
        db.create_all()