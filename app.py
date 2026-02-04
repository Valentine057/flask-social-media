import os

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from .db import get_db, init_app
from .models import User


full_project_path = os.path.dirname(os.path.realpath(__file__))

# create and configure the app
app = Flask(__name__, instance_path=full_project_path)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
)
app.app_context()

# load the instance config
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# configure the database initialization and teardown
init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-up', methods=['POST'])
def sign_up():
    user = User(
        request.form['firstName'],
        request.form['lastName'],
        request.form['email'],
        request.form['password'],
    )
    database = get_db()
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
        hashed_password = generate_password_hash(user.password)
        database.execute(
            'INSERT INTO user (first_name, last_name, email, password) VALUES (?, ?, ?, ?)',((user.first_name, user.last_name, user.email, hashed_password)),
        )
        database.commit()
        return redirect(url_for('show_login_form'))
    else:
        return error, 400

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
    