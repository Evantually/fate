from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField
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

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)