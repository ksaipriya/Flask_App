from flask import Flask,render_template,request,redirect,url_for,flash,session,logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
from models import users,myarticles

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)


# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    articles = db.session.query(myarticles).all()
    if len(articles) > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)


#Single_article
@app.route('/article/<string:id>/')
def article(id):
    article = db.session.query(myarticles).filter(myarticles.id==id).one()
    #article=result.one()
    return render_template('article.html',article=article)


#Registration_Form
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password',[
         validators.DataRequired(),
         validators.EqualTo('confirm',message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


#User_register
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        result = users(name=name,email=email,username=username,password=password)
        db.session.add(result)
        db.session.commit()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)


#User_login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        l_result = db.session.query(users.password).filter(users.username == username).all()

        if len(l_result) > 0:
            # can also use one() instead of first()
            user = db.session.query(users.password).filter(users.username == username).first()

            #Comparing password from user and database
            if sha256_crypt.verify(password_candidate, user.password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are logged in','success')
                return redirect(url_for('dashboard'))

            else:
                error = 'INVALID LOGIN'
                return render_template('login.html', error=error)

        else:
            error = 'USER NOT FOUND'
            return render_template('login.html', error=error)
    return render_template('login.html')


#check weather user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized,Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out','success')
    return redirect(url_for('login'))


#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    articles = db.session.query(myarticles).all()

    if len(articles) > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)


#Article_Form
class ArticleForm(Form):
    title = StringField('Title',[validators.Length(min=1,max=200)])
    body = TextAreaField('Body',[validators.Length(min=30)])


#add_Article
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        signature = myarticles(title=title, body=body, author=session['username'])
        db.session.add(signature)
        db.session.commit()

        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


#edit_Article
@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_article(id):

    #get article by id
    result = db.session.query(myarticles).filter(myarticles.id == id).one()

    #get form
    form = ArticleForm(request.form)

    #populate form field
    form.title.data = result.title
    form.body.data = result.body

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        #update
        db.session.query(myarticles).filter(myarticles.id == id).update({myarticles.title: title, myarticles.body: body})
        #commit
        db.session.commit()

        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


#Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    #delete query
    result=db.session.query(myarticles).filter(myarticles.id == id).delete()
    #commit
    db.session.commit()
    flash('Article Deleted','success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    db.create_all()
    app.secret_key = 'secret123'
    app.run(debug=True )

