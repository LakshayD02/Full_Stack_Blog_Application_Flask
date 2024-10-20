from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user


#Creating a flask instance

app = Flask(__name__) #For starting the flask project

#Secret Key
app.config['SECRET_KEY'] = 'mysecretkey' #For security purposes

#Adding the database
#Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#New Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:lydl02%40MYSQL@localhost/our_users'

#Initialize the database
db = SQLAlchemy(app)

#Migrating the database
migrate  = Migrate(app, db)

# class NonResizableTextArea(TextArea):
#     def __call__(self, field, **kwargs):
#         kwargs.setdefault('style', 'resize: none;')
#         return super().__call__(field, **kwargs)


# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Creating Login Form
class LoginForm(FlaskForm):
    username =  StringField('Username', validators=[DataRequired()])
    password =  PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Route for Login Page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if  form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Password', 'danger')
        else:
            flash("User doesn't Exist! Try again", 'danger')


    return render_template ('login.html', form=form)


# Route for Dashboard Page
@app.route('/dashboard',  methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
        except:
            flash("Error!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
    
    # return render_template ('dashboard.html')


# Route for Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out!")
    return redirect(url_for('login'))


#Creating blog post model
class Posts(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content =  db.Column(db.Text)
    author =  db.Column(db.String(255))
    date_posted =  db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug =  db.Column(db.String(255))
    
#Creating a posts form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author =  StringField('Author', validators=[DataRequired()])
    slug =  StringField('Slug', validators=[DataRequired()])
    submit =  SubmitField('Submit')
    

#Showin Blog Posts    
@app.route('/posts')
def posts():
    #Posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template ("posts.html", posts=posts)

#Indiviual Blog Posts
@app.route('/posts/<int:id>') #This is the route for the individual blog post
def post(id):
    post =  Posts.query.get_or_404(id)
    return render_template ("post.html", post=post)

#Edit Blog Posts
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.author = form.author.data
        post.slug = form.slug.data
        
        #Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated")
        return redirect(url_for('post', id=post.id))
    form.title.data =  post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return  render_template('edit_post.html', form=form, post=post)


#Delete Blog Posts
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete =  Posts.query.get_or_404(id)
    
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        
        #Return a message
        flash("Blog Post was Deleted")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template ("posts.html", posts=posts)
    
    except:
        #Return error Message
        flash("Error Deleting Post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template ("posts.html", posts=posts)

    
#Add a Posts Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            slug=form.slug.data
        )
        
        # Add post data to the database
        db.session.add(post)
        db.session.commit()

        # Flash a success message
        flash("Blog Post Added Successfully")
        
        # Redirect to the index page or wherever you want
        return redirect(url_for('add_post'))  # Adjust 'index' to the correct route name

    # Render the form if it's a GET request or the form is invalid
    return render_template("add_post.html", form=form)



#Creating JSON
@app.route('/date')
def get_current_data():
    favorite_game = {
        "Lakshay" : "Badminton",
        "Indoor Game" : "Chess",
        "Food" : "Burger"
    }
    # return{"Date": date.today()}
    return  favorite_game


#Creating Model
class Users(db.Model, UserMixin):
    id =  db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email  = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Password Hashing
    password_hash = db.Column(db.String(200))
    
    @property
    def password(self):
        raise AttributeError('password is not readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #Creating Stringg
    def __repr__(self):
        return '<Name %r>' % self.name
    
#Update the Database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
        except:
            flash("Error!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)  # Pass id here
    
#Deleting the record
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
        our_users = Users.query.order_by(Users.date_added).all()
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
        
    except:
        flash("Error! Could not Delete User")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

#Creating a form class
class UserForm(FlaskForm):
    name  = StringField('Name', validators=[DataRequired()])
    username =  StringField('Username', validators=[DataRequired()])
    email  = StringField('Email', validators=[DataRequired()])
    favorite_color = StringField('Profession', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField('Confirm  Password', validators=[DataRequired()])
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
    

#Creating a route decorator
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            
            #Hashing The Password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''
            flash("User added successfully")
    
    # response is returned for both GET and POST requests
    our_users = Users.query.order_by(Users.date_added).all()  # Fetch users here
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

# def index():
#     return  "<h1>Hello, World!</h1>"

@app.route('/') #Route Decorator
def index():
    first_name = "Lakshay"
    stuff = "This is <strong> my first website using flask </strong>"
    flash("Welcome to our website")
    return  render_template("index.html", first_name=first_name, stuff=stuff)

#localhost:5000/user/name
@app.route('/user/<name>')

def user(name):
    # return f"<h1>Hello, {name}!</h1>"
     return  render_template("user.html", user_name=name)
 
 #Creating custom error pages
 
#Invalid URL
@app.errorhandler(404)
def  page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def  page_not_found(e):
    return render_template("500.html"), 


#Creating password test page
@app.route('/test_pw',  methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        
        form.email.data = ''
        form.password_hash.data = ''
        
        #Lookup user ny email adsress
        pw_to_check = Users.query.filter_by(email=email).first()
        
        #Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)
        
        
        flash("Form Submitted Successfully")
    return render_template ("test_pw.html", email = email, password = password, pw_to_check=pw_to_check, passed=passed, form = form)


#Create a name page
@app.route('/name',  methods=['GET', 'POST'])
def name():
    name  = None
    form = NameForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template ("name.html", name = name, form = form)