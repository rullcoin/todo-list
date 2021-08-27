from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm
from flask_gravatar import Gravatar
import os




app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = ('secret')
Bootstrap(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    todo = relationship("Todo", back_populates='author')

class Todo(db.Model):
    __tablename__ = "todo"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="todo")
    date = db.Column(db.String(250), nullable=False)
    text = db.Column(db.Text, nullable=False)

#db.create_all()




@app.route('/')
def home():
    return render_template("index.html")

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/Login', methods= ['GET', 'POST'])
def login():
    hide_toggle = True
    log = True
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form, toggle= hide_toggle, login=log, current_user=current_user)

@app.route('/to-do', methods= ['GET', 'POST'])
def todo_list():
    return render_template('todo.html')

@app.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    sign_up = True
    hide_toggle = True
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template('sign-up.html', form=form, current_user=current_user, toggle=hide_toggle, sign_up=sign_up)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)