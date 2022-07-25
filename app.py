import os
import uuid as uuid # created unique user id
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename #to secure the name of the uploaded file
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Email, length
from flask_wtf.file import FileField
from flask_ckeditor import CKEditorField, CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import current_user, UserMixin, LoginManager, login_user, login_required, logout_user


app = Flask(__name__)

# ADD RICH TEXT EDITOR - CKEditor
ckeditor = CKEditor(app)

app.config['SECRET_KEY'] = 'b41bfb66739bd67d09342ad24f6a699deb7cbac892273d95'  # necessary for the forms

# SET LOCAL FOLDER TO SAVE FILES
UPLOAD_FOLDER = '/Users/New User/Desktop/MP3-HMABLOG/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hopedb.db'  # Add database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zvchjsqllgphgm:db745bad88a33421152e2ede1cb7ab058557eafd958aeed4490fa0d0a4a566df@ec2-3-219-52-220.compute-1.amazonaws.com:5432/djp2i5ggn6q28'  # Add database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cherlina10@localhost/hopeblog-db'


db = SQLAlchemy(app)
migrate = Migrate(app, db)


# FLASK LOGIN CONFIGURATION AND INITIALIZATION
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # where should the user be redirected if we are not logged in and a login is required


# USERS DATABASE MODEL
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    data_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)

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


# BLOG POST MODEL
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # Foreing Key
    blogger_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# POST FORM
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField('Post')


# USER FORM
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    favorite_color = StringField("Favorite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password',
                                  validators=[DataRequired(), EqualTo('password_hash2', message='Password most match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture')
    submit = SubmitField("Submit")




# LOGIN FORM
class LoginForm(FlaskForm):
    #username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")


# SEARCH FORM
# class SearchForm(FlaskForm):
#     search = StringField("Search", validators=[DataRequired()])
#     submit = SubmitField("Submit")


# Crated form CLass for the forms
class NameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def home():
    first_name = "Nicky"
    return render_template('home.html', first_name=first_name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# ADMIN PAGE
@app.route('/admin')
@login_required
def admin():
    id = current_user.id

    if id == 1:
        return render_template('admin.html')
    else:
        flash('Sorry only administrators have access to this page', 'warning')
        return redirect(url_for('dashboard'))


# Pass variable to an extended file
#@app.context_processor  # context_processor will pass a variable for any {% extends 'file.html' %}
#def base(): # this can be called anything but base as the search is inside the base file
    #form = SearchForm()
    #return dict(form=form) #dict for dictionary


# SEARCH FUNCTION
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

# LOGIN DECORATOR
@login_manager.user_loader #load users when login
def load_user(user_id):
    return Users.query.get(int(user_id))


# LOGIN PAGE
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
            flash("That User Doesn't Exist! Try Again...")

    return render_template('login.html', form=form)


# LOGOUT FUNCTION PAGE
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out!, Thank you for passing by, see you soon!... :-)', 'success')
    return redirect(url_for('home'))


# DASHBOARD PAGE
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


# INDIVIDUAL POST PAGE
@app.route('/posts/<int:id>')  # INT:ID WILL GET THE CLICKED POST TO VIEW FROM THE DB
def post(id):
    # grab all the posts from the database
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


# ALL POSTS PAGE
@app.route('/posts')
def posts():
    # grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


# TO EDIT A POST
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


# ADD POSTS TO THE DATABASE
@app.route('/add_post', methods=['GET', 'POST'])
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
        flash('Blog post added successfully')
    return render_template('add_post.html', form=form, name=name)


# DELETE POST FROM THE DATABASE
@app.route('/posts/delete/<int:id>')  # INT:ID WILL LET UD EDIT AND INDIVIDUAL POST
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.blogger.id: #check if the post to delete was created by the user
        try:
            # Delete post from the database
            db.session.delete(post_to_delete)
            db.session.commit()

            # Return message
            flash('Blog post deleted successfully')

            posts = Posts.query.order_by(Posts.date_posted)  # Query DB again
            return render_template('posts.html', posts=posts)  # and redirect to the posts page

        except:
            # If error, show message
            flash('There was a problem deleting the post')
            # an d redirect again
            posts = Posts.query.order_by(Posts.date_posted)  # Query DB again
            return render_template('posts.html', posts=posts)  # and redirect to the posts page

    else:
        flash(' You are not authorize to delete the post!')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

    # ADD USERS TO THE DATABASE
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            password = request.form.get('password_hash')
            hashed_pwd = generate_password_hash(password, method="sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pwd)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''

        flash('User Added Successfully', 'success')

    our_users = Users.query.order_by(Users.data_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


# UPDATE DATABASE RECORDS
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User updated successfully', 'success')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            flash('Error... Looks like there was a problem. Try again.')
            return render_template('update.html', form=form, name_to_update=name_to_update)

    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


# DELETE USER FROM DATABASE RECORDS
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


# NAME PAGE
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


# PASSWORD TEST FORM
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    password_hash = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# PASSWORD TEST PAGE
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


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
