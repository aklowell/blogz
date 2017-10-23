from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(12))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        verify=request.form['verify']

        existing_user=User.query.filter_by(username=username).first()
        existing_pw=existing_user.password
           
        if password != existing_pw:
            flash("Invalid password.")
            return render_template('login.html')

        if not existing_user:
            flash("No such user - please create account")
            return render_template('login.html')

        if verify != password:
            flash('Passwords do not match.')
            return render_template('login.html')

        if 'username' in session:
            flash("User already logged in!")
            return render_template('login.html')
            

        if verify == password and password==existing_pw and 'username' not in session:
            session['username'] = username
            return redirect ('/newpost')

    else:
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify=request.form['verify']
            
        if verify != password:
            flash('Passwords do not match.')
            return render_template('signup.html')

        if len(username) <= 3:
            flash("Username must have at least four characters.")
            return render_template('signup.html')

        if len(password) <= 3 or len(password) >12:
            flash("Password must have from 4 to 12 characters.")
            return render_template('signup.html')

        existing_user=User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")

        else:
            flash("Username exists")
            return render_template('signup.html')

    else:
        return render_template('signup.html')


@app.route('/blog', methods = ["POST","GET"])
def blog():


    if request.args:
        blog_id=request.args.get("id")
        
        

        #blog_owner=Blog.query.get("owner_id")
        user_id=request.args.get("userid")
        #blog_owner=User.query.filter_by(id=number).all()
     
        
        if blog_id:
            one_blog=Blog.query.get(blog_id)
            return render_template('blogentry.html',blog=one_blog)

        if user_id:
            user=User.query.get(user_id)
            
            #owner=one_blog.owner
            blogs=Blog.query.filter_by(owner=user).all()
            return render_template('userentry.html',blogs=blogs)
 
    else:
        blogs=Blog.query.order_by(Blog.id.desc()).all()
        return render_template('blogs.html', blogs=blogs)
        

@app.route('/', methods=['POST','GET'])
def index():
 
    users = User.query.order_by(User.username.asc()).all()
    return render_template('index.html', users=users)
    

@app.route('/newpost',methods=["POST", "GET"])
def add_blog():
    if request.method=="GET":
        return render_template('newpost.html')

    title_error=''
    body_error=''
 
    owner = User.query.filter_by(username=session['username']).first()

    if request.method=="POST":
        blog_title=request.form['title']
        blog_body=request.form['body']

    if len(blog_body) < 1:
        body_error="Please enter a blog entry."


    if len(blog_title) < 1:
        title_error ="Please enter a blog title."

    if not title_error and not body_error:
        new_blog=Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        query_param_url = "/blog?id=" + str(new_blog.id)
        #return render_template("blogentry.html", blog=new_blog)
        return redirect(query_param_url)

    else:

        return render_template('newpost.html', title_error=title_error, 
    body_error=body_error,blog_title=blog_title,blog_body=blog_body)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')





if __name__ == '__main__':
    app.run()