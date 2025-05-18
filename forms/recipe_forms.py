from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField,SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    image = FileField('Recipe Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit Recipe')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Recipe Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit Recipe')