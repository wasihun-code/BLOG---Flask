import secrets, os
from PIL import Image
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewPostForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user

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
@app.route("/index")
def index() -> str:
    page = request.args.get("page", 1, type=int)
    posts = Post.query.paginate(per_page=5, page=page)
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
