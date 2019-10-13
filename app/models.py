from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

user_recipes = db.Table('user_recipes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('recipe_id', db.Integer, db.ForeignKey('profession_item.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    profession_one = db.Column(db.String(128), default='None')
    profession_two = db.Column(db.String(128), default='None')
    known_recipes = db.relationship(
        'ProfessionItem', 
        secondary=user_recipes,
        primaryjoin=(user_recipes.c.user_id==id),
        backref=db.backref('item', lazy='dynamic'), lazy='dynamic'
    )

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

    def add_recipe(self, recipe):
        if not self.knows_recipe(recipe):
            self.known_recipes.append(recipe)

    def remove_recipe(self, recipe):
        if self.knows_recipe(recipe):
            self.known_recipes.remove(recipe)
    
    def knows_recipe(self, recipe):
        return self.known_recipes.filter(user_recipes.c.recipe_id).count > 0

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
    known = db.relationship(
        'User', 
        secondary=user_recipes,
        primaryjoin=(user_recipes.c.recipe_id==id),
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )

    def add_user(self, user):
        if not self.knows_user(user):
            self.known.append(user)
    
    def remove_user(self, user):
        if self.knows_user(user):
            self.known.remove(user)
    
    def knows_user(self, user):
        return self.known.filter(user_recipes.c.user_id).count > 0

class ProfessionIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    internal_id = db.Column(db.String(128))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))