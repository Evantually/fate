from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    profession_one = SelectField(
        'Profession 1',
        choices=[('None', 'None'), ('Alchemy', 'Alchemy'), ('Blacksmithing', 'Blacksmithing'), 
            ('Enchanting', 'Enchanting'), ('Engineering', 'Engineering'),
            ('Leatherworking', 'Leatherworking'), ('Tailoring', 'Tailoring')])
    profession_two = SelectField(
        'Profession 2',
        choices=[('None', 'None'), ('Alchemy', 'Alchemy'), ('Blacksmithing', 'Blacksmithing'), 
            ('Enchanting', 'Enchanting'), ('Engineering', 'Engineering'),
            ('Leatherworking', 'Leatherworking'), ('Tailoring', 'Tailoring')])
    submit = SubmitField('Submit')


    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class AddRecipeForm(FlaskForm):
    options = SelectMultipleField('Recipes', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add to my known recipes.')

class AddProfessionItemForm(FlaskForm):
    profession = SelectField(
        'Profession',
        choices=[('Alchemy', 'Alchemy'), ('Blacksmithing', 'Blacksmithing'), 
            ('Enchanting', 'Enchanting'), ('Engineering', 'Engineering'),
            ('Leatherworking', 'Leatherworking'), ('Tailoring', 'Tailoring')])
    name = StringField('Name', validators=[DataRequired()])
    learned_from = SelectField('Learned From', choices=[('trainer', 'Trainer'), ('recipe', 'Recipe')])
    skill_required = IntegerField('Skill Required', validators=[DataRequired()])
    item_quality = SelectField(
        'Item Quality',
        choices=[('Common', 'Common'), ('Uncommon', 'Uncommon'), 
            ('Rare', 'Rare'), ('Epic', 'Epic')])
    armor_class = StringField('Armor Class')
    item_slot = StringField('Item Slot')
    action = StringField('Crafting Result')
    result = IntegerField('Result Quantity')
    submit = SubmitField('Add Profession Item.')

class AddRecipeIngredientForm(FlaskForm):
    item_options = SelectField('Item', coerce=int, validators=[DataRequired()])
    ingredient_options = SelectField('Ingredient', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add Recipe Ingredient.')

class AddProfessionIngredientForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    item_quality = SelectField(
        'Item Quality',
        choices=[('Common', 'Common'), ('Uncommon', 'Uncommon'), 
            ('Rare', 'Rare'), ('Epic', 'Epic')])
    item_type = StringField('Item Type', validators=[DataRequired()])
    submit = SubmitField('Add Profession Ingredient.')

class AddDescriptionTextForm(FlaskForm):
    options = SelectField('Recipes', coerce=int, validators=[DataRequired()])
    text = StringField('text', validators=[DataRequired()])
    submit = SubmitField('Add Description Text.')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)