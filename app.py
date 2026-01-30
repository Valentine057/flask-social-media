from flask import Flask, render_template, request
from datetime import datetime

#this line initializes/creates  the Flask application
app = Flask(__name__)

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
    

#@app.route('/<language>/about-us/')
#def about_us(language):
   # if language =='en':
        #return 'This is the "About Us" page'
    #elif language == 'ib':
        #return 'Nnyin ke do page "About Us"'
    #elif language == 'fr':
        #return 'C\'est la page "About Us"'
    #else:
        #return 'We don\'t support this language'
    
#@app.route('/data/<int:how_many>')
#def user_data(how_many):
    # Build serializable data: convert datetimes to ISO strings
    #return [
        #{
            #'name': 'John Doe',
            #'email': 'john.@gmail.com',
            #'date_of_birth': datetime.now(),
        #}
    #] * how_many
    
    
# these lines indicates that we are in  "development mode"
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    