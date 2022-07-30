import os
import uuid as uuid  # created unique user id
import jwt

from time import time

from bson import ObjectId
from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  # to secure the name of the uploaded file
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Email, length
from flask_wtf.file import FileField
from flask_ckeditor import CKEditorField, CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import current_user, UserMixin, LoginManager, login_user, login_required, logout_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # for creating a timed token for email recovery
from flask_mail import Message
from flask_pymongo import PyMongo, MongoClient


app = Flask(__name__)

# ADD RICH TEXT EDITOR - CKEditor
ckeditor = CKEditor(app)


if os.path.exists("env.py"):
    import env

# APP CONFIGURATION
app.config['SECRET_KEY'] = 'b41bfb66739bd67d09342ad24f6a699deb7cbac892273d95'  # necessary for the forms



# -------------------------- DATABASE CONFIGURATION SETTINGS --------------------------------

import re

uri = os.getenv("DATABASE_URL")
# or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri


# DATABASE SETTINGS
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hopedb.db'  # Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zvchjsqllgphgm:db745bad88a33421152e2ede1cb7ab058557eafd958aeed4490fa0d0a4a566df@ec2-3-219-52-220.compute-1.amazonaws.com:5432/djp2i5ggn6q28'  # Add database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cherlina10@localhost/hopeblog-db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# -------- MONGO DB CONFIGURATION SETTINGS ------------------
# MongDB database access
cluster = MongoClient("mongodb+srv://dbAuth:Ch3rl1na10@cluster0.rqlwn.mongodb.net/?retryWrites=true&w=majority")

mongo = PyMongo()
notesdb = cluster["hopeblog"]


# MAIL CONFIGURATION
# TELL APP HOW TO SEND EMAIL
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # your mail server
# app.config['MAIL_PORT'] = 587  # number of port your email server sending emails
# app.config['MAIL_USE_TLS'] = True  # security services from the email services. Encryption
# app.config['MAIL_USE_SSL'] = False  # security services from the email services. . Encryption
# app.config['MAIL_USERNAME'] = os.environ.get('GM_USR')
# app.config['MAIL_PASSWORD'] = os.environ.get('GM_PWD')
# app.config['MAIL_DEBUG'] = True
# app.config['MAIL_DEFAULT_SENDER'] = None  # ('name', 'email') # to set the from email address by default if not specified
# app.config['MAIL_MAX_EMAILS'] = None  # limit  the amount of emails send from one request.
# app.config['MAIL_ASCII_ATTACHMENTS'] = False  # converts the file name to ASCII
# app.config['MAIL_SUPPRESS_SEND'] = False  # similar to debug. testing purposes
# app.config['TESTING'] = True  # prevent from sending email while testing

#mail = Mail(app)
# mail = Mail()
# mail.init_app(app)

# FLASK LOGIN CONFIGURATION AND INITIALIZATION
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # where should the user be redirected if we are not logged in and a login is required


# SET LOCAL FOLDER TO SAVE FILES FOR USER PROFILE
UPLOAD_FOLDER = '/Users/New User/Desktop/MP3-HMABLOG/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ----------------------------- DATABASE MODELS --------------------------------------------

# ---- BLOG POST MODEL ----
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # Foreing Key
    blogger_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# ---- USERS DATABASE MODEL -----
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    data_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Manny posts to an user
    posts = db.relationship("Posts", backref="blogger")

    # PASSWORD HASHING
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # VERIFY HASHING FUNCTION
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Created a function for how the database will be shown to the user
    def __repr__(self):
        return '<Name %r>' % self.name

    # token generation and verification functions methods for user password recovery
    # METHOD TO CREATE TOKEN FOR EMAIL RECOVERY
    def get_reset_password_token(self, expires_in=1800):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    # METHOD TO VERIFY TOKEN FOR EMAIL RECOVERY
    @staticmethod  # this tels' python not expect the self argument just the token(in this case) argument
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return Users.query.get(user_id)


# ----------------------------- FORMS CREATION --------------------------------------------

# ---- LOGIN FORM ----
class LoginForm(FlaskForm):
    # username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")


# NAME FORM Created form CLass for the forms
class NameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# ---- PASSWORD TEST FORM ----
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# ---- POST FORM ----
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Post')


#  ---- REQUEST RESET PASSWORD FORM ----
class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Request")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("There is no account with that E-Mail. You must register first", "warning")


# ---- RESET PASSWORD FORM ----
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm_password', message='Password most match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Reset Password")


# ---- SEARCH FORM ----
# class SearchForm(FlaskForm):
#     search = StringField("Search", validators=[DataRequired()])
#     submit = SubmitField("Submit")


# ----- USER FORM -----
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    favorite_color = StringField("Favorite Color")
    about_author = TextAreaField("About Me")
    password_hash = PasswordField('Password',
                                  validators=[DataRequired(), EqualTo('password_hash2', message='Password most match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("The username is already taken. Please choose another one.", "warning")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The E-Mail is already taken. Please choose different one.", "warning")


# ------------------------------------ APP ROUTES --------------------------------------------

# --- HOME ROUTE ---
@app.route('/')
def home():
    # grab the page we want do a query parameter, 1 is the default page
    page = request.args.get('page', 1, type=int)
    # grab all the posts from the database and paginate those posts
    posts = Posts.query.order_by(Posts.date_posted).paginate(page=page, per_page=2)
    return render_template('home.html', posts=posts, page=page)

# --- ABOUT ROUTE ---
@app.route('/about')
def about():
    return render_template('about.html')


# ------------------- USER ROUTES -----------------------

# --- USER NAME ---
@app.route('/user_posts/<name>')
def user(name):
    return render_template('user.html', name=name)


# --- FUNCTION TO REGISTER USER LAST LOGGED SESSION ---
# The @before_request decorator register the decorated function to be executed right before the view function
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# --- ADMIN PAGE ---
@app.route('/admin')
@login_required
def admin():
    id = current_user.id

    if id == 1:
        return render_template('admin.html')
    else:
        flash('Sorry only administrators have access to this page', 'warning')
        return redirect(url_for('dashboard'))


# --- ADD USERS TO THE DATABASE ---
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None

    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data, email=form.email.data).first()
        m_user = notesdb.users.find_one({"username": request.form.get('username')},
                                        {"email": request.form.get('email')})

        if user:
            flash('The username is already taken. Please choose another one., "warning"')

        if m_user:
            flash("User already exists", "danger")
            return redirect(url_for('add_user'))

        else:

        #if user is None:
            password = request.form.get('password_hash')
            hashed_pwd = generate_password_hash(password, method="sha256")
            user = Users(username=form.username.data,
                         first_name=form.first_name.data,
                         last_name=form.last_name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pwd)
            db.session.add(user)
            db.session.commit()

            # Code to create a new use in the MongoDB database
            register = {
                "username": request.form.get('username'),
                "email": request.form.get('email'),
                "password": generate_password_hash(request.form.get('password_hash')),
                "first_name": request.form.get('first_name'),
                "last_name": request.form.get('last_name'),
            }
            notesdb.users.insert_one(register)

            # start a session for the user
            session["users"] = request.form.get('email')
            login_user(current_user, remember=True)
            flash("Registration Successful, account created. Thank you!", "succsess")
            return redirect(url_for('home'))

        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''

        flash('User Added Successfully', 'success')

    our_users = Users.query.order_by(Users.data_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


# ---- DASHBOARD PAGE ----
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']

        # check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']  # this upload the actual file

            # variable to grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)

            # set UUID for file
            pic_name = str(uuid.uuid1()) + "_" + pic_filename

            # save the image to folder
            saver = request.files['profile_pic']

            # after save to folder change it ti string and save to db
            name_to_update.profile_pic = pic_name

            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User updated successfully', 'success')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update)
            except:
                flash('Error... Looks like there was a problem. Try again.', 'warning')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update)

        else:
            db.session.commit()
            flash('User updated successfully', 'success')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)

    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    return render_template('dashboard.html')


# --- DELETE USER FROM DATABASE RECORDS ---
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
            flash('User deleted successfully!', 'success')

            our_users = Users.query.order_by(Users.data_added)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)

        except:
            flash('There was a problem deleting user, try again', 'warning')
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    else:
        flash("Sorry you can't delete that user!", "danger")
        return redirect(url_for('dashboard'))


# --- LOGIN DECORATOR ---
@login_manager.user_loader  # load users when login
def load_user(user_id):
    return Users.query.get(int(user_id))


# --- LOGIN PAGE ---
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password/Login - Please Try Again!", 'warning')
        else:
            flash("That User Doesn't Exist! Try Again...", 'warning')

    return render_template('login.html', form=form)


# --- LOGOUT FUNCTION PAGE ---
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out!, Thank you for passing by, see you soon!... :-)', 'success')
    return redirect(url_for('home'))


# --- NAME PAGE ---
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    # Validated form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template('name.html', name=name, form=form)


# --- PASSWORD TEST PAGE ---
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # Validated form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        # clear form
        form.email.data = ''
        form.password_hash.data = ''

        # query the database
        pw_to_check = Users.query.filter_by(email=email).first()

        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password=password, form=form, pw_to_check=pw_to_check,
                           passed=passed)


# --- RESET PASSWORD REQUEST PAGE ---
@app.route('/reset_pwd', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Please check your email for the instructions to reset your password', 'info')
            return redirect(url_for('login'))
        else:
            flash('This email is not register, please sign up!', 'danger')
            return redirect(url_for('add_user'))

    return render_template('reset_request.html', form=form, title='Reset Password')


# --- RESET PASSWORD PAGE ---
@app.route('/reset_pwd/<token>', methods=['GET', 'POST'])
def reset_pwd_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # check for the reset token
    user = Users.verify_reset_password_token(token)

    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = request.form.get('password')
        hashed_pwd = generate_password_hash(password, method="sha256")
        user.password = hashed_pwd
        db.session.commit()
        flash("Your password has been reset successfully!", "success")
    return render_template('reset_pwd_token.html', form=form, title='Reset Password')


# --- UPDATE USER DATABASE RECORDS ---
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.first_name = request.form['first_name']
        name_to_update.last_name = request.form['last_name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User updated successfully', 'success')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            flash('Error... Looks like there was a problem. Try again.', 'warning')
            return render_template('update.html', form=form, name_to_update=name_to_update)

    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)



# ------------------------------------- NOTES ROUTES -------------------------------------

# --- NOTES PAGE ---
@app.route('/notes')
@login_required
def notes():
    notes = list(notesdb.notes.find())
    users = notesdb.users.find()
    return render_template("notes.html", user=current_user, notes=notes, users=users)


# --- ADD NOTE PAGE ---
@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():

    if request.method == 'POST':
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        note = {
            'category_name': request.form.get('category_name'),
            'note_title': request.form.get('note_title'),
            'note': request.form.get('note'),
            is_urgent: is_urgent,
            'due_date': request.form.get('due_date'),
            'created_by': session['users'],
        }
        notesdb.notes.insert_one(note)
        flash("New note added successfully!")
        return redirect(url_for("main.notes"))
    categories = notesdb.categories.find().sort("category_name", 1)
    return render_template("add_note.html", user=current_user, categories=categories)


# --- EDIT NOTE PAGE ---
@app.route('/edit_note/<note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):

    if request.method == 'POST':
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        updated_note = {
            'category_name': request.form.get('category_name'),
            'note_title': request.form.get('note_title'),
            'note': request.form.get('note'),
            is_urgent: is_urgent,
            'due_date': request.form.get('due_date'),
            'created_by': session['users'],

        }
        notesdb.notes.replace_one({"_id": ObjectId(note_id)}, updated_note)
        flash("Note updated successfully!")
        return redirect(url_for("notes"))

    note = notesdb.notes.find_one({"_id": ObjectId(note_id)})
    categories = notesdb.categories.find().sort("category_name", 1)
    return render_template("edit_note.html", note=note, user=current_user, categories=categories)


# --- DELETE NOTE  ---
@app.route('/delete_note/<note_id>', methods=['GET', 'POST'])
@login_required
def delete_note(note_id):
        notesdb.notes.remove_one({"_id": ObjectId(note_id)})
        flash("Note delete successfully!")
        return redirect(url_for("main.notes"))




# ----------------------------- POSTS ROUTES ----------------------------------

# --- ADD POST TO THE DATABASE ---
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    name = None
    form = PostForm()

    if form.validate_on_submit():
        blogger = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, blogger_id=blogger, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        # add post tho the database
        db.session.add(post)
        db.session.commit()

        # Return message
        flash('Blog post added successfully', 'success')
    return render_template('add_post.html', form=form, name=name)


# --- ALL POSTS PAGE ---
@app.route('/posts')
@login_required
def posts():
    # grab the page we want do a query parameter, 1 is the default page
    page = request.args.get('page', 1, type=int)
    # grab all the posts from the database and paginate those posts
    posts = Posts.query.order_by(Posts.date_posted).paginate(page=page, per_page=2)
    return render_template('posts.html', posts=posts)


# --- DELETE POST FROM THE DATABASE ---
@app.route('/posts/delete/<int:id>')  # INT:ID WILL LET UD EDIT AND INDIVIDUAL POST
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.blogger.id:  # check if the post to delete was created by the user
        try:
            # Delete post from the database
            db.session.delete(post_to_delete)
            db.session.commit()

            # Return message
            flash('Blog post deleted successfully', 'success')

            posts = Posts.query.order_by(Posts.date_posted)  # Query DB again
            return render_template('posts.html', posts=posts)  # and redirect to the posts page

        except:
            # If error, show message
            flash('There was a problem deleting the post', 'warning')
            # an d redirect again
            posts = Posts.query.order_by(Posts.date_posted)  # Query DB again
            return render_template('posts.html', posts=posts)  # and redirect to the posts page

    else:
        flash(' You are not authorize to delete the post!', 'danger')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


# --- EDIT A POST ---
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])  # INT:ID WILL LET UD EDIT AND INDIVIDUAL POST
@login_required
def edit_post(id):
    # grab the posts from the database
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data

        # Update post on the database
        db.session.add(post)
        db.session.commit()

        flash('Post has be updated successfully')
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.blogger_id:

        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug

        return render_template('edit_post.html', form=form)

    else:
        flash(' You are not authorize to edit this post!', 'danger')
        posts = Posts.query.order_by(Posts.date_posted)  # Query DB again
        return render_template('posts.html', posts=posts)  # and redirect to the posts page


# ---- INDIVIDUAL POST PAGE ----
@app.route('/posts/<int:id>')
@login_required# INT:ID WILL GET THE CLICKED POST TO VIEW FROM THE DB
def post(id):
    # grab all the posts from the database
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


# --- USER POSTS PAGE ---
@app.route('/user/<first_name>')
@login_required
def user_posts(first_name):
    # grab the page we want do a query parameter, 1 is the default page
    page = request.args.get('page', 1, type=int)

    # Query the db for the user
    user = Users.query.filter_by(first_name=first_name).first_or_404()

    # grab all the posts from the database and paginate those posts
    user_posts = Posts.query.filter_by(blogger=user).order_by(Posts.date_posted).paginate(page=page, per_page=2)
    return render_template('user_posts.html', first_name=first_name, user_posts=user_posts)


#  ---- SEARCH FUNCTION ----
# -- Pass variable to an extended file --
# @app.context_processor  # context_processor will pass a variable for any {% extends 'file.html' %}
# def base(): # this can be called anything but base as the search is inside the base file
# form = SearchForm()
# return dict(form=form) #dict for dictionary

# @app.route('/search', methods=['POST'])
# def search():
#     form = SearchForm()
#     user_search = Posts.query
#     if form.validate_on_submit():
#         #get data from the search form
#         post.searched = form.search.data
#         # qquery the DB
#         search_found = user_search.filter(Posts.content.like('%' + post.searched + '%'))
#         search_found = user_search.order_by(Posts.title).all()
#
#         return render_template('search.html', form=form, searched=post.searched, search_found=search_found)


# ----------------------------- ERROR ROUTES ----------------------------------

# ---- Invalid URL ----
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# ----- Internal Server Error ----
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


# ----------------------------- FUNCTIONS ----------------------------------

# FUNCTION TO SEND EMAILS
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    msg = Message(subject='Password Reset Request',
                  sender=('HMA-Blog', 'noreply@gmail.com'),
                  recipients=[user.email])

    msg.body = f''' 
Dear {{ user.username }},

To reset your password click on the following link:

{ url_for('reset_pwd_token', token=token, _external=True) }

If you have not requested a password reset simply ignore this message.

Sincerely,

The HMA Blog Team
'''
    msg.html = f'''
<p>Dear {{ user.username }},</p>
<p>To reset your password 
<a href="{{ url_for('reset_password', token=token, _external=True) }}">click here</a>.
</p>
<p>Alternatively, you can paste the following link in your browser's address bar:</p>
<p>{{ url_for('reset_password', token=token, _external=True) }}</p>
<p>If you have not requested a password reset simply ignore this message.</p>
<p>Sincerely,</p>
<p>The HMA Blog Team</p>
'''

    # mail.add_recipient('')
    # with app.open_resource('name of file') as file:
    # msg.attach('filename', 'MIME type of file i.e image/jpeg', file.read())
    # PARAMETER WE CAN HAVE IN THE MESSAGE FUNCTION
    # msg = Message(
    #     subject = ' ',
    #     recipients = [],
    #     body = '',
    #     html = '',
    #     sender = '',
    #     cc = [],
    #     bcc = [],
    #     reply_to = [],
    #     date = 'date',
    #     charset = ''
    # )

    mail.send(msg)

    return flash('Message sent', 'info')



if __name__ == '__main__':
    app.run(debug=True)
