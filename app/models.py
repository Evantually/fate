from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

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
        secondaryjoin=(user_recipes.c.recipe_id == 'profession_item.id'),
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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('profession_item.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('profession_ingredient.id'))
    quantity = db.Column(db.Integer)

class ProfessionItem(SearchableMixin, db.Model):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    profession = db.Column(db.String(64))
    image_link = db.Column(db.String(128))
    internal_id = db.Column(db.String(128))
    name = db.Column(db.String(128))
    learned_from = db.Column(db.String(128))
    skill_required = db.Column(db.Integer)
    item_quality = db.Column(db.String(64))
    armor_class = db.Column(db.String(64), default='None')
    item_slot = db.Column(db.String(64), default='None')
    action = db.Column(db.String(256))
    result = db.Column(db.Integer)
    known = db.relationship(
        'User', 
        secondary=user_recipes,
        primaryjoin=(user_recipes.c.recipe_id==id),
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )
    description_text = db.relationship('DescriptionText', backref='description', lazy='dynamic')

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
    item_quality = db.Column(db.String(64))
    item_type = db.Column(db.String(64))

class DescriptionText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    item_id = db.Column(db.Integer, db.ForeignKey('profession_item.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))