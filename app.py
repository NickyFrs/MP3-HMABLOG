from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, EqualTo, Email

app = Flask(__name__)

app.config['SECRET_KEY'] = 'b41bfb66739bd67d09342ad24f6a699deb7cbac892273d95'


# Crated form CLass
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
