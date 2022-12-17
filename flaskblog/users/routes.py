from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from flaskblog.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    RequestResetForm,
    ResetPasswordForm,
)
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if request.method == "POST" and form.validate_on_submit():
        # Debugging purpose
        print("Form Validated")

        # Creating hash for password: security reasons
        hashed_pw = bcrypt.generate_password_hash(form.password.data)

        # Instantiating a user object to save to databse
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_pw
        )

        # Adding user to database
        db.session.add(user)
        db.session.commit()

        # Display success message
        flash("Account created successfully! You can now Login", category="success")

        # Redirect them to login page
        return redirect(url_for("users.login"))

    # On get request, create a form object and render the template for users to register
    return render_template("register.html", title="Register to get started", form=form)


@users.route("/login", methods=["GET", "POST"])
def login() -> str:

    # Create a login form instance
    form = LoginForm()

    # if all fields of the form are correct, then it is validated
    if form.validate_on_submit():

        # Query the user by the entered username
        user = User.query.filter_by(username=form.username.data).first()

        # if the query returned a result
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            # then login to the website and display message
            login_user(user=user, remember=form.remember.data)
            flash("You've Logged in successfully", "success")

            # If user wanted to login to account directly
            if request.args.get("next") == "/account":

                # Debugging purpose
                print(request.args.get("next"))

                # redirect them to the account route
                return redirect(url_for("users.account"))

            # redirect them to home page
            return redirect(url_for("main.index"))

        # if no user exists with the entered credentials
        flash(
            "Login Unsuccessful. Please check username and password and try again.",
            "danger",
        )

    # either in get request of failure to provide correct credential serve the template
    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():

    # Instantiate update account form
    form = UpdateAccountForm()

    # if form data is valid and is going to be submitted
    if form.validate_on_submit():

        if form.picture.data:
            current_user.image = save_picture(form.picture.data)

        # Change username and email fo current user
        current_user.username = form.username.data
        current_user.email = form.email.data

        # Commit the changes to the database
        db.session.commit()

        # Display success message to the suer
        flash("Account Updated successflly", category="success")

        # Redirect it to the page itself to avoid get post redirect
        return redirect(url_for("users.account"))

    # If the user is just getting the account page
    elif request.method == "GET":

        # Put place holder on username and email
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for("static", filename="profile_pictures/" + current_user.image)
    return render_template("account.html", title="Account", image=image, form=form)

@users.route("/reset_password", methods=["GET", "POST"])
def request_password():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instruction to reset your password.",
            category="info",
        )
        return redirect(url_for("users.login"))

    return render_template("request_password.html", title="Reset Password", form=form)


@users.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.verify_reset_token(token)

    if not user:
        flash("That token is either expired or invalid.", category="warning")
        return redirect(url_for("users.request_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash(
            "Password reset successful. You can now login with the new password of yours.",
            category="success",
        )
        return redirect(url_for("users.login"))

    return render_template("reset_password", title="Reset Password", form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)
