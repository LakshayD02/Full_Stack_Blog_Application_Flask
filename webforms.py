from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from flask_wtf.file  import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


#Creating Search Form
class SearchForm(FlaskForm):
    searched =  StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Login')
    

# Creating Login Form
class LoginForm(FlaskForm):
    username =  StringField('Username', validators=[DataRequired()])
    password =  PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
    
    #Creating a posts form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author =  StringField('Author')
    slug =  StringField('Slug', validators=[DataRequired()])
    submit =  SubmitField('Submit')
    
    
#Creating a form class
class UserForm(FlaskForm):
    name  = StringField('Name', validators=[DataRequired()])
    username =  StringField('Username', validators=[DataRequired()])
    email  = StringField('Email', validators=[DataRequired()])
    favorite_color = StringField('Profession', validators=[DataRequired()])
    about_author = TextAreaField('About Author')
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField('Confirm  Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit =  SubmitField('Submit')
    
    
    #Creating a form class
class NameForm(FlaskForm):
    name  = StringField('What is your name?', validators=[DataRequired()])
    # email  = StringField('Email?', validators=[DataRequired()])
    # favorite_color = StringField('Favourite Colour', validators=[DataRequired()])

    submit =  SubmitField('Submit')
    

 #Creating a form class
class PasswordForm(FlaskForm):
    email  = StringField('What is your Email?', validators=[DataRequired()])
    password_hash  = PasswordField('What is your Password?', validators=[DataRequired()])
    # favorite_color = StringField('Favourite Colour', validators=[DataRequired()])
    submit =  SubmitField('Submit')
    