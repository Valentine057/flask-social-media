import os

from flask import Flask, render_template, request

from . import db


full_project_path = os.path.dirname(os.path.realpath(__file__))

# create and configure the app
app = Flask(__name__, instance_path=full_project_path)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
)

# load the instance config
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# configure the database initialization and teardown
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign-up', methods=['POST'])
def sign_up():
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']

    return f"Welcome to our app, {first_name} {last_name}"

@app.route('/sign-up', methods=['GET'])
def show_sign_up_form():
    return render_template('sign-up.html')


# these lines indicates that we are in  "development mode"
# they will only execute if we run the app by executing this file directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    