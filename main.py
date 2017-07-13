#I need a docstring here, apparently.

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogroot@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1234567890'

#create a new class that can be managed by sqlalchemy & store blogs in a db
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner): #name instead of title?
        self.title = title #or should this be self.name = name? 
        self.body = body
        self.owner = owner


#create a new class that can be managed by sqlalchemy & store users in a db
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


#write a function that requires login before accessing the blog & newpost pages
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


#write a function that allows a user to login & go to their blog page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged in')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


#write a function that allows a user to register as a user
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            flash('This username is already taken', 'error')

    return render_template('register.html')


#a function to let you logout
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


#a function to allow the user to post a blog
@app.route('/newpost', methods=['POST', 'GET']) 
def post_blog():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if blog_title == '' or blog_body == '':
            flash('Please fill out both fields before submitting.', 'error')
            
            return redirect('/newpost')
        
        else:
            owner = User.query.filter_by(email=session['email']).first()
            new_entry = Blog(blog_title, blog_body, owner)
            db.session.add(new_entry)
            db.session.commit()

            return redirect('/')

    else:
        return render_template('newpost.html')

@app.route('/thisblog')
def view_thisblog():
    thisblog = Blog.query.filter_by(id=id).first()

    return render_template('thisblog.html')


@app.route('/')
def list_blogs():

    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all() #owner=owner specifies that this blog belongs to this user(owner)
    
    return render_template('bloglist.html', title='Get writing!', blogs=blogs)


if __name__ == '__main__':
    app.run()