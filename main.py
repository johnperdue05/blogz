from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'jasd5433523'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect ('/blog')

@app.route('/blog')
def blog():
    id = request.args.get('id')
    if not id:
        posts = Blog.query.all()
        return render_template('blog.html',title="Build a Blog", 
        posts=posts)
    post = Blog.query.filter_by(id=id).first()
    return render_template('entry.html', title=post.title, post=post)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
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
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()


        return redirect('/blog?id=' + str(new_post.id))


if __name__ == '__main__':
    app.run()