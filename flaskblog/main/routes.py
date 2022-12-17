from flask import render_template, request, Blueprint
from flaskblog.models import Post

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/index")
def index() -> str:
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("main/index.html", posts=posts)


@main.route("/about")
def about() -> str:
    return render_template("main/about.html", title="About")