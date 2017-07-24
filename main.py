'''This is a blog app that allows users to publish and view blog entries'''

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
    allowed_routes = ['login', 'register', 'bloglist', 'index']
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
        if user and user.password != password:
            flash('User password incorrect', 'error')
        if not user:
            flash('User does not exist', 'error')

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

            if len(password)< 3 or len(email)< 3:
                flash('Please use a password that is at least 3 characters long', 'error')
                return render_template('register.html')
            elif verify != password:
                flash('Please make sure passwords match', 'error')
                return render_template('register.html')
            else:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/')
        else:   
            flash('This username is already taken', 'error')
    
    return render_template('register.html') #keep this here as the main route


#a function to let you logout
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/thisblog')
def view_thisblog():
    blog_id = request.args.get('id')
    if blog_id: 
        thisblog = Blog.query.filter_by(id=blog_id).first()
        return render_template('thisblog.html', blog=thisblog)


@app.route('/bloglist', methods=['POST', 'GET'])
def list_all_blogs():  #lists all blogs by all authors

    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('bloglist.html', title='All blogs', blogs=blogs, users=users)


#to display blogs by a single user 
@app.route('/singleuser')
def singleuser():

    user = request.args.get('id')
    if user:        
        #owner = User.query.filter_by(email= request.form['email']).first()
        blogs = Blog.query.all()   
        return render_template('singleuser.html', user=user, blogs=blogs)


#index page will list all blog authors with names linked
@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='All users', users=users)


#a function to order of the blogs by primary key
def sort_blogs():
    
    all = Blog.query.get('id')
    list = all.sort()
    return render_template('thisblog.html', list)


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

            return render_template('thisblog.html', blog=new_entry)

    else:
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()