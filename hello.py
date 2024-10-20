from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NameForm, SearchForm
from flask_ckeditor  import CKEditor
from werkzeug.utils  import secure_filename
import uuid as uuid
import os



#Creating a flask instance

app = Flask(__name__) #For starting the flask project

#Adding CKeditor
ckeditor = CKEditor(app)

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

UPLOAD_FOLDER  = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


#Passing things to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)



@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    searched = ""

    if form.validate_on_submit():
        # Get the data from submitted form
        searched = form.searched.data

        # Query the Database for content, title, and author name
        posts = posts.filter(
            (Posts.content.like(f'%{searched}%')) |
            (Posts.title.like(f'%{searched}%')) |
            (Users.name.like(f'%{searched}%'))
        ).join(Users).order_by(Posts.title).all()

    return render_template("search.html", form=form, searched=searched, posts=posts)
    
#Create Admin Page

@app.route('/admin') #Route Decorator
@login_required
def admin():
    id =  current_user.id
    if id==27:
        return render_template('admin.html')
    else:
        flash("You must be the admin to access this page")
        return redirect(url_for('dashboard'))


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


#Route for dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
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
        name_to_update.about_author = request.form['about_author']

        # Check for profile picture upload
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic and profile_pic.filename != '':
                # Grab Image Name
                pic_filename = secure_filename(profile_pic.filename)
                # Set UUID
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                # Save the Image
                profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                # Change it to string to save it to the database
                name_to_update.profile_pic = pic_name

        # If no new picture was uploaded, keep the existing one
        # This is handled by not changing `name_to_update.profile_pic` if `profile_pic` is not valid.

        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
        except Exception as e:
            flash(f"Error! {str(e)}")
            db.session.rollback()  # Rollback the session in case of an error
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)


    # return render_template ('dashboard.html')


# Route for Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out!")
    return redirect(url_for('login'))


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
        # post.author = form.author.data
        post.slug = form.slug.data
        
        #Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id or current_user.id==27:
        form.title.data =  post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return  render_template('edit_post.html', form=form, post=post)
    
    else:
        flash("You are not allowed to edit this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template ("posts.html", posts=posts)


# Delete Blog Posts
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    user_id = current_user.id

    # Check if the poster exists before accessing its id
    if (post_to_delete.poster is not None and user_id == post_to_delete.poster.id) or user_id == 27:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog Post was Deleted")
        except Exception as e:
            # Log the error (optional) and return an error message
            print(f"Error deleting post: {e}")  # You can log this to a file if needed
            flash("Error Deleting Post")
    else:
        flash("You are not allowed to delete this post")

    # Fetch the updated list of posts
    posts = Posts.query.order_by(Posts.date_posted).all()
    return render_template("posts.html", posts=posts)
    
#Add a Posts Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        poster =  current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
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

    
#Update the Database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete(id):
    if id == current_user.id:
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

    else:
        flash("You cannot delete the user")
        return redirect(url_for('dashboard'))
            

#Creating a route decorator
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            profile_pic = form.profile_pic.data
            pic_name = None
            
            if profile_pic:
                pic_filename = secure_filename(profile_pic.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            else:
                pic_name = 'default_profile_pic.png'  # Default image

            user = Users(username=form.username.data, name=form.name.data,
                          email=form.email.data, favorite_color=form.favorite_color.data,
                          profile_pic=pic_name, password_hash=hashed_pw)

            db.session.add(user)
            db.session.commit()
            flash("User added successfully")

    our_users = Users.query.order_by(Users.date_added).all()
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

# def index():
#     return  "<h1>Hello, World!</h1>"

@app.route('/')  # Route Decorator
def index():
    first_name = "Lakshay"
    stuff = "This is <strong>my first website using Flask</strong>"

    # Check if the welcome message has already been shown
    if 'welcome_message_shown' not in session:
        flash("Welcome to our website")
        session['welcome_message_shown'] = True  # Set the session variable

    return render_template("index.html", first_name=first_name, stuff=stuff)

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


#Creating password test page/User Authentication
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        
        form.email.data = ''
        form.password_hash.data = ''
        
        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        
        # Check if user exists before checking password
        if pw_to_check:
            # Check hashed password
            passed = check_password_hash(pw_to_check.password_hash, password)
        else:
            flash("User with this email does not exist.", "danger")
            return redirect(url_for('test_pw'))  # Redirect to the same page to show the message

        flash("Form Submitted Successfully")
        
    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)


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




#FOR DATABASE

#Creating blog post model
class Posts(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content =  db.Column(db.Text)
    # author =  db.Column(db.String(255))
    date_posted =  db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug =  db.Column(db.String(255))
    # Foriegn key for the user (Refer to the primary key of the user)
    poster_id =  db.Column(db.Integer, db.ForeignKey('users.id'))



    
#Creating Model
class Users(db.Model, UserMixin):
    id =  db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(200))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)

    #Users can have many posts
    posts = db.relationship('Posts', backref='poster', lazy=True)
    
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
    