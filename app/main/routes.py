from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, AddRecipeForm, SearchForm
from app.models import User, ProfessionItem, ProfessionIngredient, RecipeIngredient
from app.main import bp

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    users = User.query.filter(User.id != current_user.id).all()
    for user in users:
        if user.profession_one != 'None':
            profession_one_recipes = user.known_recipes.filter_by(profession=user.profession_one).order_by(ProfessionItem.skill_required.desc()).all()
            user.max_skill_prof_one = profession_one_recipes.first().skill_required
        if user.profession_two != 'None':
            profession_two_recipes = user.known_recipes.filter_by(profession=user.profession_two).order_by(ProfessionItem.skill_required.desc()).all()
            user.max_skill_prof_two = profession_two_recipes.first().skill_required
    return render_template('index.html', title='Home', users=users)

@bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    recipes = user.known_recipes
    profession_one_recipes = recipes.filter_by(profession=user.profession_one).order_by(ProfessionItem.skill_required).all()
    profession_two_recipes = recipes.filter_by(profession=user.profession_two).order_by(ProfessionItem.skill_required).all()
    for recipe in profession_one_recipes:
        recipe.ingredients = RecipeIngredient.query.filter_by(item_id=recipe.id).all()
        for item in recipe.ingredients:
            item.name = ProfessionIngredient.query.filter_by(id=item.ingredient_id).first().name
    for recipe in profession_two_recipes:
        recipe.ingredients = RecipeIngredient.query.filter_by(item_id=recipe.id).all()
        for item in recipe.ingredients:
            item.name = ProfessionIngredient.query.filter_by(id=item.ingredient_id).first().name
    return render_template('user.html', user=user, profession_one=user.profession_one, 
                        profession_two=user.profession_two, profession_one_recipes=profession_one_recipes, 
                        profession_two_recipes=profession_two_recipes)

@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.profession_one.default = current_user.profession_one
        form.profession_two.default = current_user.profession_two
        form.profession_one.process(request.form)
        form.profession_two.process(request.form)
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@bp.route('/recipes/<profession>')
def recipes(profession):
    profession = profession[0].upper() + profession[1:].lower()
    recipes = ProfessionItem.query.filter_by(profession=profession).filter(ProfessionItem.skill_required>0).order_by(ProfessionItem.skill_required).all()
    for recipe in recipes:
        recipe.ingredients = RecipeIngredient.query.filter_by(item_id=recipe.id).all()
        for item in recipe.ingredients:
            item.name = ProfessionIngredient.query.filter_by(id=item.ingredient_id).first().name
    return render_template('profession_recipes.html', recipes=recipes)

@bp.route('/add_recipes/<profession>', methods=['GET','POST'])
@login_required
def add_recipes(profession):
    profession = profession[0].upper() + profession[1:].lower()
    if profession not in (current_user.profession_one, current_user.profession_two):
        flash(f'You do not have {profession} listed as one of your professions.')
        return redirect(url_for('main.edit_profile'))
    form = AddRecipeForm()
    form.options.choices = [(recipe.id, recipe.name) for recipe in ProfessionItem.query.filter_by(profession=profession).filter(ProfessionItem.skill_required>0).order_by(ProfessionItem.skill_required).all()]
    if form.validate_on_submit():
        for item in form.options.data:
            ProfessionItem.query.filter_by(id=item).first().known.append(current_user)
            current_user.known_recipes.append(ProfessionItem.query.filter_by(id=item).first())
            db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('recipe_selection.html', profession=profession, form=form)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    recipes, total = ProfessionItem.search(g.search_form.q.data)
    return render_template('search.html', title='Search', recipes=recipes)