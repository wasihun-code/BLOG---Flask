from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, login_required

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
    return render_template("index.html", posts=posts)


@app.route("/about")
def about() -> str:
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    if request.method=="POST" and form.validate_on_submit():
        # Debugging purpose
        print("Form Validated")
        
        # Creating hash for password: security reasons
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        
        # Instantiating a user object to save to databse
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        
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
            flash("You've Logged in successfully", 'success')
            
            # If user wanted to login to account directly
            if request.args.get('next') == '/account':
                
                # Debugging purpose
                print(request.args.get('next'))
                
                # redirect them to the account route
                return redirect(url_for("account"))

            # redirect them to home page
            return redirect(url_for("index"))
        
        # if no user exists with the entered credentials
        flash("Login Unsuccessful. Please check username and password and try again.", "danger")
        
    # either in get request of failure to provide correct credential serve the template
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account")