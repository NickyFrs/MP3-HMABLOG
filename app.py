from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, EqualTo, Email
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'b41bfb66739bd67d09342ad24f6a699deb7cbac892273d95' # necessary for the forms

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hopedb.db' # Add database

db = SQLAlchemy(app)

# DATABASE MODEL
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    data_added = db.Column(db.DateTime(), default=datetime.utcnow)

    # Created a function for hpw the database will be shown to the user
    def __repr__(self):
        return '<Name %r>' % self.name




class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")


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


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash('User Added Successfully')
    our_users = Users.query.order_by(Users.data_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


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
