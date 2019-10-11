from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    profession_one = db.Column(db.String(128))
    profession_two = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('profession_item.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('profession_ingredient.id'))
    quantity = db.Column(db.Integer)

class ProfessionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profession = db.Column(db.String(64))
    image_link = db.Column(db.String(128))
    internal_id = db.Column(db.String(128))
    name = db.Column(db.String(128))
    learned_from = db.Column(db.String(128))
    skill_required = db.Column(db.Integer)
    action = db.Column(db.String(256))
    result = db.Column(db.Integer)

class ProfessionIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    internal_id = db.Column(db.String(128))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))