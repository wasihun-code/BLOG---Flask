from PIL import Image
import secrets, os, datetime
from flask_mail import Message
from flaskblog.models import User, Post
from flaskblog import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from flaskblog.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    NewPostForm,
    RequestResetForm,
    ResetPasswordForm,
)


@app.route("/")
@app.route("/index")
def index() -> str:
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", posts=posts)


@app.route("/about")
def about() -> str:
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for("login"))

    # On get request, create a form object and render the template for users to register
    return render_template("register.html", title="Register to get started", form=form)


@app.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("account"))

            # redirect them to home page
            return redirect(url_for("index"))

        # if no user exists with the entered credentials
        flash(
            "Login Unsuccessful. Please check username and password and try again.",
            "danger",
        )

    # either in get request of failure to provide correct credential serve the template
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


def save_picture(form_picture_data):

    # Grab the file extension from the form data
    _, file_extension = os.path.splitext(form_picture_data.filename)

    # Generate a random file name to avoid filename conflict
    random_file_name = secrets.token_hex(8)

    # Concatenate random file name and file extension
    picture_fn = random_file_name + file_extension

    # extract and store the picture path
    picture_path = os.path.join(app.root_path, "static/profile_pictures/", picture_fn)

    # Input a custom output size
    output_size = (125, 125)

    # Prepare the image to resize: open it
    i = Image.open(form_picture_data)

    # Resize the image
    i.thumbnail(output_size)

    # save the picture on the extracted path
    i.save(picture_path)

    # return the file name later to update it on the database
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
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
        return redirect(url_for("account"))

    # If the user is just getting the account page
    elif request.method == "GET":

        # Put place holder on username and email
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = url_for("static", filename="profile_pictures/" + current_user.image)
    return render_template("account.html", title="Account", image=image, form=form)


@app.route("/posts/new", methods=["GET", "POST"])
def new_post():

    form = NewPostForm()

    if form.validate_on_submit():

        # Create post
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )

        # Add the database and commit the changes
        db.session.add(post)
        db.session.commit()

        # Display success message
        flash("Post created successefully!", category="success")

        # And redirect user to home page
        return redirect(url_for("index"))

    return render_template(
        "create_post.html", title="New Post", form=form, legend="New Post"
    )


@app.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = NewPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.date_posted = datetime.datetime.utcnow()
        db.session.commit()
        flash("Post has been updated", category="success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@app.route("/posts/<int:post_id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", category="success")
    return redirect(url_for("index"))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=2)
    )
    return render_template("user_post.html", posts=posts, user=user)


def send_reset_email(user):

    token = user.get_reset_token()
    message = Message(
        "Password reset request", sender="noreply@gmail.com", recipients=[user.email]
    )
    message.body = f"""
        Follow the link bellow to reset your password
        { url_for('reset_password', token=token, _external=True) }

        Ignore this message if you didn't request for a password change.
    """
    
    # DEBUGGING PURPOSE
    print("SENDING MESSAGE")
    mail.send(message)


@app.route("/reset_password", methods=["GET", "POST"])
def request_password():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            "An email has been sent with instruction to reset your password.",
            category="info",
        )
        return redirect(url_for("login"))

    return render_template("request_password.html", title="Reset Password", form=form)


@app.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    user = User.verify_reset_token(token)

    if not user:
        flash("That token is either expired or invalid.", category="warning")
        return redirect(url_for("request_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash(
            "Password reset successful. You can now login with the new password of yours.",
            category="success",
        )
        return redirect(url_for("login"))

    return render_template("reset_password", title="Reset Password", form=form)
