from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'lkjagasd09joqifn'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            if not user:
                flash('User does not exist', 'error')
            elif user.password != password:
                flash('User password incorrect', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if len(username) < 3 or len(password) < 3:
            if len(username) < 3:
                flash('Please enter a valid username between 3 and 20 characters in length', 'error')
            if len(password) < 3:
                flash('Please enter a valid password between 3 and 20 characters in length', 'error')
        elif password == verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return "<h1>Duplicate user</h1>"
        else:
            flash('Passwords must match')

    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',title="Bloggerz!", users=users)

@app.route('/blog')
def blog():
    id = request.args.get('id')
    userId = request.args.get('user')
    if not id:
        if userId:
            posts = Blog.query.filter_by(owner_id = userId).order_by(Blog.pub_date.desc()).all()
        else:
            posts = Blog.query.order_by(Blog.pub_date.desc()).all()
        return render_template('blog.html',title="Build a Blog", 
        posts=posts)
    if userId:
        posts = Blog.query.filter_by(owner_id=userId).order_by(Blog.pub_date.desc()).all()
        return render_template('blog.html', posts)
    post = Blog.query.filter_by(id=id).first()
    return render_template('entry.html', post=post)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''
        if not title or not body:
            if not title:
                title_error = "Please give your post a title"
            if not body:
                body_error = "And where is the body?"
            return render_template('newpost.html', title=title, title_error=title_error, body=body, body_error=body_error)
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()


        return redirect('/blog?id=' + str(new_post.id))

@app.route('/logout')
def logout():
    del session['username']
    flash('Logged out')
    return redirect('/blog')

if __name__ == '__main__':
    app.run()