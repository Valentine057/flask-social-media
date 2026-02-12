import os
import sqlite3 

from flask import Flask, session, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from .db import init_db, db, close_db
from .models import User


full_project_path = os.path.dirname(os.path.realpath(__file__))

# create and configure the app
app = Flask(__name__, instance_path=full_project_path)

# load the instance config
app.config.from_pyfile('config.py', silent=True)
app.app_context()

# ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# configure the database initialization and teardown
db.init_app(app)
app.cli.add_command(init_db)
app.teardown_appcontext(close_db)


@app.route('/')
def index():
    user=None
    
    if "email" in session:
        user = db.session.execute(db.select(User).filter_by(email=session["email"])).scalar_one()
        # This is another way to query a user
        # user= User.query.filter(User.email == session["email"]).first() 
        
    return render_template('index.html', current_user=user)


@app.route('/sign-up', methods=['POST'])
def sign_up():
    user = User(
        request.form['firstName'],
        request.form['lastName'],
        request.form['email'],
        request.form['password'],
    )
    error = None

    if not user.first_name:
        error = 'Please enter your first name'
    elif not user.last_name:
        error = 'Please enter your last name'
    elif not user.email:
        error = 'Please enter your email'
    elif not user.password:
        error = 'Please choose a password'

    if error is None:
        user.password = generate_password_hash(user.password)
       
        try:       
            db.session.add(user)
            db.session.commit()
        except sqlite3.IntegrityError: 
            error= "This email already exists"
        else:
            return redirect(url_for('show_login_form'))
    
    return error, 400

@app.post('/login')
def login():
    email= request.form['email']
    password= request.form['password']
    error= None

    user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one()

    if user is None:
        error= "incorrect email"
    elif not check_password_hash(user["password"], password):
        error= "password don't match"
    
    if error is None:
        session["email"]=user.email
        return redirect(url_for('index'))
    else:
        return error, 401


@app.route('/sign-up', methods=['GET'])
def show_sign_up_form():
    return render_template('sign-up.html')

@app.get('/login')
def show_login_form():
    return render_template('login.html')


# these lines indicates that we are in  "development mode"
# they will only execute if we run the app by executing this file directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    