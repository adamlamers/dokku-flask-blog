from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from jinja2 import Markup
from models import User, Post, postgres_db
from functools import wraps
import json
import bcrypt
import markdown
import datetime
import peewee
from mdx_gfm import GithubFlavoredMarkdownExtension as GithubMarkdown

app = Flask(__name__)
app.config.from_object("config.Config")

auth = LoginManager()
auth.init_app(app)
auth.login_view = "login"
auth.login_message = "You must be logged in to access that page."
auth.login_message_category = "danger"

@app.context_processor
def recent_post_context_processor():
    return { 'recent_posts': Post.select().order_by(Post.created_at.desc()).limit(3)}

@app.context_processor
def top_tags_context_processor():
    values = {}

    all_tags = {}
    for post in Post.select():
        for tag in post.tags.split(';'):
            if tag in all_tags:
                all_tags[tag] += 1
            else:
                all_tags[tag] = 1

    sorted_tags = ((k, all_tags[k]) for k in sorted(all_tags, key=all_tags.get, reverse=True))

    values['top_tags'] = list(sorted_tags)[0:10]
    return values

@app.template_filter('Markdown')
def filter_markdown(raw_markdown):
    return Markup(markdown.markdown(raw_markdown, extensions=[GithubMarkdown()]))

def admin_required(f):
    @wraps(f)

    def wrapper(*args, **kwargs):
        if not current_user.admin:
            flash("You need administrator privileges to access this page.", "danger")
            return redirect(url_for('blog'))
        return f(*args, **kwargs)

    return wrapper

@auth.user_loader
def user_loader(uid):
    user = None
    try:
        user = User.get(User.id == uid)
    except User.DoesNotExist:
        pass

    return user

@app.before_first_request
def setup_database():
    postgres_db.create_tables([User, Post], safe=True)


@app.route('/init')
def init_user():
    try:
        User.create(name="admin", password=bcrypt.hashpw(b"password", bcrypt.gensalt()), admin=True)
    except peewee.IntegrityError:
        pass

@app.route('/')
def index():
    return redirect(url_for('blog'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login/go', methods=["POST"])
def do_login():

    username = request.form.get("username", False)
    password = request.form.get("password", False)

    if username and password:
        try:
            u = User.get(User.name == username)
            if bcrypt.hashpw(password.encode(), u.password.encode()) == u.password.encode():
                login_user(u)
                requested_page = request.args.get('next')
                print(current_user.name)
                return redirect(requested_page or url_for('blog'))
            else:
                flash("Username or password incorrect.", "danger")
                return redirect(url_for('login'))
        except User.DoesNotExist:
            flash("User does not exist.", "danger")
    else:
        flash("Username and password required.", "danger")

    return redirect(url_for('login'))

@app.route('/blog')
def blog():
    posts = Post.select().order_by(Post.created_at.desc()).limit(5)
    return render_template('blog_list.html', posts=posts)

@app.route('/post/<int:pid>')
def post(pid):
    post = None
    try:
        post = Post.get(Post.id == pid)
    except Post.DoesNotExist:
        abort(404)

    return render_template('post_view.html', post=post)

@app.route('/tag/<tag>')
def view_tag(tag):
    matches = Post.select().where(Post.tags.contains(tag)).limit(5)
    return render_template('blog_list.html', posts=matches)

@app.route('/admin/preview', methods=["POST"])
@login_required
@admin_required
def preview():
    html = markdown.markdown(request.form['post-content'], extensions=[GithubMarkdown()])
    return html

@app.route('/admin/posts/compose')
@login_required
@admin_required
def compose():
    return render_template('compose.html', editing=False)

@app.route('/admin/posts/edit/<pid>')
@login_required
@admin_required
def admin_edit_post(pid):
    post = None

    try:
        post = Post.get(Post.id == pid)
    except Post.DoesNotExist:
        abort(404)

    return render_template('compose.html', editing=True, pid=pid, post=post)

@app.route('/admin/posts/save', methods=["POST"])
@login_required
@admin_required
def admin_save_post():

    edit_id = request.form.get('post-edit-id')
    title = request.form.get('post-title')
    content = request.form.get('post-content')
    description = request.form.get('post-description')
    tags = request.form.get('post-tags')

    if not edit_id:
        post = Post(title=title,
                    content=content,
                    tags=tags,
                    description=description,
                    posted_by=current_user.id)
        post.save()
    else:
        try:
            post = Post.get(Post.id == edit_id)

            post.title = title
            post.content = content
            post.description = description
            post.tags = tags
            post.updated_at = datetime.datetime.now()

            post.save()
        except Post.DoesNotExist:
            abort(404)

    return redirect(url_for('admin_post_list'))

@app.route('/admin/posts')
@login_required
@admin_required
def admin_post_list():
    return render_template('post_list.html', posts=Post.select())

@app.route('/admin/posts/delete', methods=["POST"])
@login_required
@admin_required
def admin_post_delete():

    id_to_delete = request.form.get("id")

    if not id_to_delete:
        abort(400)

    if id_to_delete:
        try:
            post_to_delete = Post.get(Post.id==id_to_delete)
            post_to_delete.delete_instance()
        except Post.DoesNotExist:
            abort(404)

    return json.dumps({ "message" : "Deleted post.", "status" : "success"})


@app.route('/admin/users')
@login_required
@admin_required
def admin_user_list():
    return render_template('user_list.html', users=User.select().limit(20))

@app.route('/admin/users/create')
@login_required
@admin_required
def admin_user_create():
    return render_template('edit_user.html', editing=False)

@app.route('/admin/users/edit/<uid>')
@login_required
@admin_required
def admin_user_edit(uid):
    try:
        user_to_edit = User.get(User.id == uid)
    except User.DoesNotExist:
        abort(404)
    return render_template('edit_user.html', editing=True, user=user_to_edit)

@app.route('/admin/users/save', methods=["POST"])
@login_required
@admin_required
def admin_user_save():
    username = request.form.get('user-name')
    password = request.form.get('user-password')
    is_admin = request.form.get('user-is-admin') == 'on'
    edit_id = request.form.get('user-edit-id')

    if edit_id:

        try:
            user_to_edit = User.get(User.id == edit_id)

            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            user_to_edit.name = username
            user_to_edit.password = hashed_pw
            user_to_edit.admin = is_admin

            user_to_edit.save()
            flash("User edited", "success")
        except User.DoesNotExist:
            abort(404)

    else:

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        u = User.create(name=username, password=hashed_pw, admin=is_admin)
        flash("User created!", "success")

    return redirect(url_for('admin_user_list'))

@app.route('/admin/users/delete', methods=["POST"])
@login_required
@admin_required
def admin_user_delete():
    status = {}
    status['ok'] = True

    if 'id' not in request.form:
        abort(400)

    id_to_delete = request.form.get('id', None)

    if id_to_delete:
        try:
            user_to_delete = User.get(User.id == id_to_delete)
            user_to_delete.delete_instance()
        except User.DoesNotExist:
            status['ok'] = False

    return json.dumps(status)

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    return render_template("admin_settings.html")

@app.route('/admin/settings/save')
@login_required
@admin_required
def admin_settings_save():
    return ''

if __name__ == '__main__':
    app.debug = True
    app.run()

