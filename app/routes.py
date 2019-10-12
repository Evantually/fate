from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User, ProfessionItem, RecipeIngredient, ProfessionIngredient
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddRecipeForm
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Evan'}
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.profession_one = form.profession_one.data
        current_user.profession_two = form.profession_two.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.profession_one.default = current_user.profession_one
        form.profession_two.default = current_user.profession_two
        form.profession_one.process(request.form)
        form.profession_two.process(request.form)
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/recipes/<profession>')
def recipes(profession):
    profession = profession[0].upper() + profession[1:].lower()
    recipes = ProfessionItem.query.filter_by(profession=profession).filter(ProfessionItem.skill_required>0).order_by(ProfessionItem.skill_required).all()
    for recipe in recipes:
        recipe.ingredients = RecipeIngredient.query.filter_by(item_id=recipe.id).all()
        for item in recipe.ingredients:
            item.name = ProfessionIngredient.query.filter_by(id=item.ingredient_id).first().name
    return render_template('profession_recipes.html', recipes=recipes)

@app.route('/add_recipes/<profession>', methods=['GET','POST'])
@login_required
def add_recipes(profession):
    profession = profession[0].upper() + profession[1:].lower()
    if profession not in (current_user.profession_one, current_user.profession_two):
        flash(f'You do not have {profession} listed as one of your professions.')
        return redirect(url_for('edit_profile'))
    form = AddRecipeForm()
    form.options.choices = [(recipe.id, recipe.name) for recipe in ProfessionItem.query.filter_by(profession=profession).filter(ProfessionItem.skill_required>0).order_by(ProfessionItem.skill_required).all()]
    if form.validate_on_submit():
        for item in form.options.data:
            ProfessionItem.query.filter_by(id=item).first().known.append(current_user)
            current_user.known_recipes.append(ProfessionItem.query.filter_by(id=item).first())
            db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('recipe_selection.html', profession=profession, form=form)