from flaskblog import app
from flask import render_template, url_for, flash, redirect
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]


@app.route("/")
@app.route("/home")
@app.route("/index")
def index() -> str:
    return render_template("index.html", posts=posts)


@app.route("/about")
def about() -> str:
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash("Account created successfully for {form.username}!", category="success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register to get started", form=form)


@app.route("/login")
def login() -> str:
    form = LoginForm()
    return render_template("login.html", title="Login to BLOG", form=form)
