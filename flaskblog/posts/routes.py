import datetime
from flaskblog.models import Post
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog.posts.forms import NewPostForm
from flaskblog import db
from flask_login import login_required, current_user


posts = Blueprint("posts", __name__)


@posts.route("/posts/new", methods=["GET", "POST"])
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

        # And redirect post to home page
        return redirect(url_for("main.index"))

    return render_template(
        "create_post.html", title="New Post", form=form, legend="New Post"
    )


@posts.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@posts.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
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
        return redirect(url_for("posts.post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@posts.route("/posts/<int:post_id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", category="success")
    return redirect(url_for("main.index"))


@posts.route("/post/<string:postname>")
def post_posts(postname):
    page = request.args.get("page", 1, type=int)
    post = post.query.filter_by(postname=postname).first_or_404()
    posts = (
        Post.query.filter_by(author=post)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=2)
    )
    return render_template("post_post.html", posts=posts, post=post)
