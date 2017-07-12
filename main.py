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

    id = db.Column(db.Integer, primary_key = True)
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
            return redirect('/blog')
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


#this route should list blogs via get method - as in the base.html file
@app.route('/blog') 
def list_blogs():

    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    blog_title = request.form['title']

    return render_template('blog.html')


#a function to allow the user to post a blog
@app.route('/newpost', methods=['POST', 'GET']) 
def post_blog():
     
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['title'] #check again if this should say 'name' instead of 'title'
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.filter_by(owner=owner).all()

    return render_template('newpost.html')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first() 
    
    if request.method == 'POST':   #if request is a post (if it came from submitting the form)
        blog_name = request.form['blog']   #then we want to grab the data out of the user's input 
        new_blog = Blog(blog_name, owner)  #create new Blog object 
        db.session.add(new_blog) #add it to future commits
        db.session.commit()   #commit to database as a persistent object

    blogs = Blog.query.filter_by(owner=owner).all() #owner=owner specifies that this blog belongs to this user(owner)
    return render_template('blog.html', title='Get writing!', blogs=blogs)


if __name__ == '__main__':
    app.run()