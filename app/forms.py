"""Import libraries necessary"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets import TextArea


class SearchForm(FlaskForm):
    """Defining the search form fields"""
    searched = StringField('searched', validators=[
                           DataRequired(message="Data Missing")])


class UpdateUser(FlaskForm):
    """Defining the updateUser form fields"""
    username = StringField(
        'Username*', validators=[DataRequired(message="Data Missing")])
    name = StringField(
        'Name*', validators=[DataRequired(message="Data Missing")])
    email = StringField(
        'Email*', validators=[DataRequired(message="Data Missing")])
    age = IntegerField('Age')
    relationship_status = StringField('Relationship Status')
    major = StringField('Major')
    student_bio = TextAreaField('Bio')
    year_of_study = IntegerField('Year of study')
    birthdate = DateField('Birthdate')
    linkedIn = StringField('LinkedIn')
    instagram = StringField('Instagram')
    snapchat = StringField('Snapchat')
    nationality = StringField('Nationality')


class RegisterForm(FlaskForm):
    """Defining the register form fields"""
    username = StringField('username', validators=[
                           DataRequired(message="Data Missing")])
    name = StringField('name', validators=[
                       DataRequired(message="Data Missing")])
    email = StringField('email', validators=[
                        DataRequired(message="Data Missing")])
    relationship_status = TextAreaField('relationship_status')
    student_bio = TextAreaField('student_bio')
    password_hash = TextAreaField('Password', validators=[DataRequired(
        message="Data Missing"), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = TextAreaField('Confirm Password', validators=[
                                   DataRequired(message="Data Missing")])


class LoginForm(FlaskForm):
    """Defining the login form fields"""
    email = StringField('email', validators=[
                        DataRequired(message="Data Missing")])
    password = PasswordField('Password', validators=[
                             DataRequired(message="Data Missing")])


class PostForm(FlaskForm):
    """Defining the post form fields"""
    title = StringField('Title', validators=[
                        DataRequired(message="Data Missing")])
    content = StringField('Content', validators=[DataRequired(
        message="Data Missing")], widget=TextArea())
    slug = StringField('Slug', validators=[
                       DataRequired(message="Data Missing")])
